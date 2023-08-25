import os
import sys
import re
import json

       
class Colors:
    '''--------------------------------Класс содержит ANSI коды цвета и формата текста -------------------------------'''
    def __init__(self, console:bool):
        (self.ideColor, self.consoleColor)[console]() # Выбераем какие цвета использовать и вызываем соответствующий метод

    def ideColor(self)->None:
        self.colors = {'SYNC':'SYNC',
                       'stdin': 'stdin',
                       'BUILTIN': 'BUILTIN',
                       'STRING': 'STRING',
                       'console':'console',
                       'COMMENT': 'COMMENT',
                       'stdout':'stdout',
                       'TODO':'TODO',
                       'stderr':'stderr',
                       'hit':'hit',
                       'DEFINITION':'DEFINITION',
                       'KEYWORD':'KEYWORD',
                       'ERROR':'ERROR'}
    def consoleColor(self)->None:
        self.colors = {
            'bg': {
                'default': '49;',
                'black': '40;',
                'red': '41;',
                'green': '42;',
                'yellow': '43;',
                'blue': '44;',
                'purple': '45;',
                'cyan': '46;',
                'light_gray': '47;',
                'dark_gray': '100;',
                'light_red': '101;',
                'light_green': '102;',
                'light_yellow': '103;',
                'light_blue': '104;',
                'pink': '105;',
                'light_cyan': '106;',
                'white': '107;'
                },
            'text': {
                'default': '39;',
                'black': '30;',
                'red': '31;',
                'green': '32;',
                'yellow': '33;',
                'blue': '34;',
                'purple': '35;',
                'cyan': '36;',
                'light_gray': '37;',
                'dark_gray': '90;',
                'light_red': '91;',
                'light_green': '92;',
                'light_yellow': '93;',
                'light_blue': '94;',
                'pink': '95;',
                'light_cyan': '96;',
                'white': '97;'
                },
            'bold': {False: '21;', True: '1;'},
            'underlined': {False: '24;', True: '4;'}
            }
  
class Style(Colors):
    '''--------------------------------Класс формирующий ANSI стили для вывода-------------------------------'''
    def __init__(self, style:str, style_path:str, console: bool, ANSI: bool):
        
        Colors.__init__(self, console)
        self._stylePath = style_path
     
        getStyle = (self._getStyleIDE, self._getStyleNoANSI )[console] # Выбераем метод  для консоли или ide
        getStyle = (getStyle, self._getStyleANSI)[ANSI] # Выбераем метод поддерживает ли терминал ANSI
        typeStyle = ("ide", "console")[ANSI] # Выбераем тип стилей
        
        # Проверяем существует ли файл стилей
        if os.path.exists(style_path):
            style_config = self._getStyleConfig(style_path, style, typeStyle)
        else:
            style_config = self._getDefaultStyleConfig(style_path, style, typeStyle)
            
        style = getStyle(style_config)
        self.__dict__.update(style) # записываем атрибуты стилей полученые из файл



    def __getattr__(self, name):
        cls = self.__class__.__name__
        message = f'\nВ классе:  "{cls}" отсутствует атрибут: "{name}"\nПроверьте файл стилей: '#"{self._stylePath}"'
        Error =  type('AttributeError',(AttributeError,),{})
        raise Error(message)

        
    def _getStyleANSI(self, style_config):
        style = {}
        for key, color  in style_config.items():
            key, *name = key.split('_') # разбиваем ключевое слово на ключ к стилям(text,bg,bold...) и имя атрибута
            name = '_'.join(name) or "_"
            val = self.colors.get(key, {}).get(color, '')
            style.update({name: style.get(name, '\033[21;22;24;25;27;28;') + val })# '\033[21;22;24;25;27;28;' ANSI код отключающий все стили
            
        [style.update({key: color[:-1]+'m'}) for key, color in style.items()]
        return style
    
    def _getStyleIDE(self, style_config):
        return style_config
    
    def _getStyleNoANSI(self, style_config):
        return dict((key, '') for key, color  in style_config.items() if key)
    
    def _getDefaultStyleConfig(self, style_path:str, style:str, typeStyle:str)->dict:
        style_config = {
            "console":{
                    "clasic":{
		"bg_console":"black",
		"text_console":"white",
		"underlined_console":0,
		"bold_console":0,
		"text_info":"green",
		"bold_info":0,
		"bg_info":"black",
		"underlined_info":0,
		"text_err":"red",
		"bold_err":0,
		"bg_err":"black",
		"underlined_err":0,
		"underlined_title":1,
		"bg_title":"white",
		"text_title":"black",
		"bold_title":0,
		"bg_line1":"dark_gray",
		"text_line1":"white",
		"bold_line1":0,
		"underlined_line1":1,
		"bg_line2":"light_gray",
		"text_line2":"black",
		"bold_line2":0,
		"underlined_line2":1
                                }
                            },
        "ide":{
                "clasic": {
                    'console': 'console',
                    'info': 'STRING',
                    'err': 'stderr',
                    'title':'KEYWORD',
                    'line1':'BUILTIN',
                    'line2':'DEFINITION'}
                }
            }
        
        ''' ide color: ['SYNC', 'stdin', 'BUILTIN', 'STRING', 'console', 'COMMENT', 'stdout', 'TODO', 'stderr', 'hit', 'DEFINITION', 'KEYWORD', 'ERROR']      '''
        
        os.makedirs('/'.join(style_path.replace("\\",'/').split('/')[:-1]),exist_ok=True) # проверяем есть ли путь, если нет создаем
        with open(style_path, "a+") as file:
                file.seek(0)
                data = json.dumps(style_config).replace(', ',',\n').replace('{','{\n').replace('}','\n}')# форматируем строку json чтоб в фале была более читаемой
                file.write(data) # записываем словарь в файл
                file.close()
        styles = style_config.get(typeStyle) # получаем словарь стилей в зависимоти от типа терминала
        return styles.get(style, styles.get("clasic",{})) # возвращаем нужный стиль
    
    def _getStyleConfig(self, style_path:str, style:str, typeStyle:str)->dict:
        with open(style_path, 'r') as file:
            styles = json.load(file).get(typeStyle,{})
            style = styles.get(style, styles.get("clasic",{}))
            file.close()
        return style

    
class Echo(Style):
    '''-----------------Класс кастомного вывода в консоль-----------------------------'''
    def __init__(self, style:str, style_path:str, console:bool, ANSI:bool,  pageSize:int, separator = ' | '):
        self.style = Style(style, style_path, console, ANSI)
        self._sep = separator
        self._print = (self._printIDE, self._printConsole)[console]
        
    def _printConsole(self, string:str, color:str, sep='\n')->None:
        print(color + string + self.style.console,sep=sep)

    def _printIDE(self, sting:str, color:str, sep='\n')->None:
        sys.stdout.shell.write(sting + sep, color)
        
    def printTable(self, list_table:iter, max_length_columns:list)->None:
        # Форматируем колонки по ширине и выравниваем по центру
        format_string = self._sep.join("{:^"+str(m)+"}" for m in max_length_columns) 
        for ix, line in enumerate(list_table):
            if not ix:
                self._print(format_string.format(*line), self.style.title)
            elif ix%2:
                self._print(format_string.format(*line), self.style.line1)
            else:
                self._print(format_string.format(*line), self.style.line2)           

    def printMessage(self, string:str):
            self._print(string, self.style.console)
            
    def printInfo(self, string:str):
            self._print(string, self.style.info)

    def printErr(self, string:str):
            self._print(string, self.style.err)
        
class Table:
    '''---------------------Класс для работы с txt файлами формата таблиц-------------------------------'''
    def __init__(self, file_path, titles: list, id_line:bool , RAM = True, page_size = 10, separaor = "\t"):
        self.pageSize = page_size
        self._sep = separaor
        self.pageNumber = 0
        self.titles = titles
        self._idLine = id_line
        self.file_path = file_path
        self.maxLengths = [0]*len(titles)
        # В зависимоти от того используем ли оперативку используем различные методы
        if RAM:
            self.addLine = self._addLineInList
            self.getPage = self._getPageFromList
            self.getAll = self._getAllFromList
            self.searchMath = self._searchMathFromList
            self.searchID = self._searchIDFromList
            self.searchKey = self._searchKeyFromList
            self.updateLine = self._updateLineFromList
        else:
            self.addLine = self._addLineInFile
            self.getPage = self._getPageFromFile
            self.getAll = self._getAllFromFile
            self.searchMath = self._searchMathFromFile
            self.searchID = self._searchIDFromFile
            self.searchKey = self._searchKeyFromFile
            self.updateLine = self._updateLineFromFile
        # Проверяем существует ли файл таблицы
        if os.path.exists(file_path):
            self._listLines = []
            self.__config(RAM)
        else:
            self._listLines = self._createFile(RAM)
            self._updateMaxLength(self.titles)
            self.NumLastLine = 0
            
    '''--------------------------------------Config метотды-------------------------------'''
    def __config(self, RAM:bool)->None:
        data = self._getAllFromFile()
        count_col = len(self.titles)
        for ix, line in enumerate(data):
            # проверяем сответствует ли количество колонок в строке количеству заголоков
            if count_col == len(line):
                self._updateMaxLength(line)
                # если используем оперативку записываем строки в список
                if RAM:
                   self._listLines.append(line)
            else:
                # если не соответствет количеству колонок вызываем исключение с сообщением что файл был изменен.
                del data
                sys.tracebacklimit = 0
                raise type('FormatError',(Exception,),{})("Не верный формат файла!\n    В строке: <"+ str(ix)+'> Файла: "' + self.file_path + '" ошибка.')

            self.NumLastLine = ix 
        
    def _createFile(self, RAM:bool)->list:
        os.makedirs('/'.join(self.file_path.replace("\\",'/').split('/')[:-1]),exist_ok=True)
        with open(self.file_path, 'a+') as file:
                file.seek(0)
                file.write(self._sep.join(self.titles)+"\n")
                file.close()
        return ([],[self.titles])[RAM]

    '''--------------------------------------Метод обновления максимальной длинны столбцов-------------------------------'''
    def _updateMaxLength(self, line:list)->None:
        temp = list(map( max, self.maxLengths, map(len,line) )) # новая максимальная длинна колонок
        # очищаем и добавляем новый список чтобы сохранить ссылку на объект
        self.maxLengths.clear() 
        self.maxLengths.extend(temp)
        return

    '''--------------------------------------Методы добавляюще строку в таблицу-------------------------------'''
    
    def _addLineInFile(self, list_line:list)->bool:
        
        list_line = ( [], [str(self.NumLastLine+1)] )[self._idLine] + list_line # используется ли id строк
        #проверяем соответсвует ли заголовкам
        if len(list_line) != len(self.titles):
            return False
        self.NumLastLine +=1
        self._updateMaxLength(list_line) # обновляем список максимальной длинны столбцов
        with open(self.file_path,'a+') as file:
                file.seek(0, 2)
                file.write(self._sep.join(list_line)+'\n')
                file.close()
        return True
        
                
    def _addLineInList(self, list_line:list)->bool:
        result = self._addLineInFile(list_line)
        if result:
            list_line = ( [], [str(self.NumLastLine)] )[self._idLine] + list_line # используется ли id строк
            self._listLines.append(list_line)
        return result
        
    '''------------------------------Методы возвращающие все из таблицы -------------------------------'''
    
    def _getAllFromFile(self) -> 'generator obj: [[],[],...]':
        #функция генератор чтения из фала по строкам
        with open(self.file_path,'r') as file:
            file.seek(0)
            for line in file:
                yield line.strip().split(self._sep)
            file.close()
            
    
    def _getAllFromList(self) -> list:
        return  self._listLines

    
    '''--------------------------------------Методы поиска-------------------------------'''
    # Поиск по совпадению(Независим от регистра и учитывает пробелы)
    # при поиске " Aл" найдет ООО Aлые паруса, а "Aл" найдет еще Алену и Алексндра с РусАЛочкой
    def _searchMathFromList(self, string:str)->list:
        search_list = []
        string = string.lower()
        for line in self._listLines:
            if string in ",".join(line).lower():
                search_list.append( line )
        if search_list:
            return [self.titles] + search_list
        return []
    
    # Поиск по совпадению
    def _searchMathFromFile(self, string:str)->list:
        search_list = []
        string = string.lower()
        with open(self.file_path,'r') as file:
            file.seek(0)
            for line in file:
                if string in line.lower(): 
                    search_list.append( line.strip().split(self._sep) )
        if search_list:
            return [self.titles] + search_list
        return []

    
    # Поиск по номеру строки
    def _searchIDFromFile(self, num_line:int)->list:
        search_line = []
        with open(self.file_path,'r') as file:
            file.seek(0)
            for ix, line in enumerate(file):
                if ix == num_line:
                    search_line.append(line.strip().split(self._sep))
        return [self.titles] + search_line
    
    # Поиск по номеру строки
    def _searchIDFromList(self, num_line:int)->list:
        return [self.titles] + self._listLines[num_line: num_line+1]

    
    # Поиск по ключевым словам строки(Зависим от регистра ) при поиске " Aл" не найдет ничего.
    def _searchKeyFromList(self, list_keys:list)->list:
        search_dict = {}
        for line in self._listLines:
            weight = sum( el.strip() in line for el in list_keys)
            if weight:
                search_dict.update( {tuple(line) : weight } )
        max_weight = max(search_dict.values() or [0])
        search_list =  [key for key, w in search_dict.items() if w==max_weight]
        if max_weight:
            return [self.titles] + search_list
        else:
            return []
        
    # Поиск по ключевым словам строки 
    def _searchKeyFromFile(self, list_keys:list)->list:
        search_dict = {}
        with open(self.file_path, 'r') as file:
            file.seek(0)
            for line in file:
                line = line.strip().split(self._sep)
                weight = sum( el.strip() in line for el in list_keys)
                if weight:
                    search_dict.update( {tuple(line) : weight } )
                    
            max_weight = max(search_dict.values() or [0])
            search_list =  [key for key, w in search_dict.items() if w==max_weight]
            if max_weight:
                return [self.titles] + search_list
            else:
                return []   
        
    '''--------------------------------------Методы обновления строк-------------------------------'''
    def _updateLineFromFile(self, num_line:int, list_line:list)->bool:
        result = False
        temp_path = '.\\temp_file.txt'
        list_line = ( [], [str(num_line)] )[self._idLine] + list_line # используется ли id строк
        #проверяем соответсвует ли заголовкам
        if len(list_line) != len(self.titles) and self.NumLastLine >= num_line:
            return result
        self._updateMaxLength(list_line) # обновляем список максимальной длинны столбцов
        # создаем временный файл с изменениями
        with open(self.file_path, 'r') as file, open(temp_path, 'a+') as temp:
            file.seek(0)
            temp.seek(0)
            for ix, line in enumerate(file):
                if ix == num_line:
                    temp.write(self._sep.join(list_line)+'\n')
                    result = True
                else:
                    temp.write(line)
            file.close()
            temp.close()
        # заменяем старый файл на новый
        os.replace(temp_path, self.file_path)
        return result
    
    def _updateLineFromList(self, num_line:int, list_line:list)->bool:
        
        list_line = ( [], [str(num_line)] )[self._idLine] + list_line # используется ли id строк
        # проверяем соответсвует ли заголовкам иначе -> False
        if len(list_line) != len(self.titles) and self.NumLastLine >= num_line:
            return False
        self._updateMaxLength(list_line) # обновляем список максимальной длинны столбцов
        self._listLines[num_line] = list_line # обновляем список строк в памяти
        # записываем в файл из памяти
        with open(self.file_path, 'w') as file:
            file.seek(0)
            file.writelines([self._sep.join(line)+'\n' for line in self._listLines])
            file.close()
        return True
    
    '''--------------------------------------Методы страниц-------------------------------'''
    def _getPageFromFile(self) -> list: 
        line_start = self.pageNumber*self.pageSize+1
        line_stop = (self.pageNumber+1)*self.pageSize+1
        list_lines = []
        with open(self.file_path,'r') as file:
            file.seek(0) 
            for ix, line in enumerate(file,1):
                if line_start   <= ix  <= line_stop:
                    list_lines.append(line.strip().split(self._sep))
                elif ix >line_stop:
                    break
            file.close()
        return [self.titles]+list_lines
    
    def _getPageFromList(self) -> list: 
        line_start = self.pageNumber*self.pageSize+1
        line_stop = (self.pageNumber+1)*self.pageSize+1
        return [self.titles] + self._listLines[line_start: line_stop]
    
    def nextPage(self)->int:
        max_page = self.NumLastLine//self.pageSize + (self.NumLastLine % self.pageSize >0)-1
        self.pageNumber = min(self.pageNumber+1, max_page)
        return self.pageNumber
    
    def backPage(self)->int:
        self.pageNumber = max( self.pageNumber-1, 0)
        return self.pageNumber
    
    def updatePage(self, num:int)->int:
        max_page = self.NumLastLine//self.pageSize + (self.NumLastLine % self.pageSize >0)-1
        self.pageNumber = max(min(num, max_page),0)
        return self.pageNumber



        
class ConfigApp:
    def __init__(self,  title_app:str, config_path='.\\config\\config.json',
                 console_width = 120, console_height = 40, buffer_cols = 150, buffer_lines = 9001,
                 **kw):
        
        self.console_width = console_width
        self.console_height = console_height
        self.buffer_cols = buffer_cols
        self.buffer_lines = buffer_lines
        self.title_app = title_app
        try:
            self.console = sys.stdout.shell.write("","")
        except:
            self.console = True
            
        self.ANSI = hasattr(sys.stdout, 'buffer') and sys.stdout.buffer.isatty()
        configData = dict(
            title_app = title_app,
            console_width = console_width,
            console_height = console_height,
            buffer_cols = buffer_cols,
            buffer_lines = buffer_lines
        )
        
        configData.update(kw)
        
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as file:
                file.seek(0)
                configData.update( json.load(file) )
                file.close()
        else:
            os.makedirs('/'.join(config_path.replace("\\",'/').split('/')[:-1]),exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as file:
                file.seek(0)
                s = json.dumps(configData).replace(', ',',\n').replace('{','{\n').replace('}','\n}')
                file.write(s)
                file.close()
        self.__dict__.update(configData) # записываем атрибуты в экземпляр класса из конфиг файла
        self.OS = self._getOS()
        self._commandsDict = self._getCommands(self.OS)# получаем словарь команд для текущей ОС
        if self.ANSI:
            self.__commandTitle(self.title_app)
            self.__commandBufferSize(self.buffer_cols, self.buffer_lines)
            self.__commandResize(self.console_width, self.console_height)

    def _getCommands(self, OS):
        dct = {
            "win":{
                        "title": 'echo "\033]0;{title}\007"', # изменить заголовок консоли
                        "buffer": 'mode con: cols={cols} lines={lines}', # размер буфера консоли
                        "resize": 'echo \033[8;{h};{w}t' # размер окна консоли
                        },
            "linux":{
                        "title": 'echo -ne "\033]0;{title}\007"', # изменить заголовок терминала
                        "buffer": 'stty rows {lines} && stty cols {cols}', # размер буфера консоли
                        "resize": 'echo \033[8;{h};{w}t' # размер окна консоли
                        },
            "macos":{
                        "title": 'echo -n -e "\033]0;{title}\007"', # изменить заголовок терминала
                        "resize": 'printf " \e[8;{h};{w}t"' # размер окна терминала
                        }
            }
        return dct.get(OS,{})
    
    def _getOS(self)->str:
        dctOS = {"win32": "win","win64": "win", "darwin":"macos", "linux": "linux"}
        return dctOS.get(sys.platform, None)

    '''---------------Метод проверки безопасности при выпонении консольных команд-------------'''
    def _security(self, target)->str:
        pattern = r'^[a-zA-Zа-яА-Я0-9 _.Ёё]{1,30}$'
        target = str(target)    
        if re.match(pattern, target):
          return target
        else:
            print(f"Строка: {target} содержит недопустимые символы!")
            return ''
        
    '''---------------Методы консольных команд-------------'''
    
    def __commandResize(self, w:int, h:int):
        _ = os.system(
            self._commandsDict.get("resize",'').format(
                h=int( self._security(h) ), w=int( self._security(w) )
                )
            )

    def __commandBufferSize(self, cols:int, lines:int):
        _ = os.system(
            self._commandsDict.get("buffer",'').format(
                cols=self._security(cols),  lines=self._security(lines)
                )
            )
                  
    def __commandTitle(self, title:str):
        _ = os.system(self._commandsDict.get("title",'').format( title=self._security(title) ))

        
