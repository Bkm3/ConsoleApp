import re
from ConsoleApp import ConfigApp,Echo,Table

                  
##1.                   Вывод постранично записей из справочника на экран
##2.                   Добавление новой записи в справочник
##3.                   Возможность редактирования записей в справочнике
##4.                   Поиск записей по одной или нескольким характеристикам


class Contacts(ConfigApp,Echo,Table):
    '''Класс приложения телефонной книги использует модуль ConsoleApp,
для кастомного вывода в консоль и работы с текстовыми фалами формата таблиц'''
    def __init__(self,config_path):
        config = ConfigApp("ContactsApp",config_path=config_path, style_path = '.\\Styles\\styles.json', style = 'clasic',
                           table_path= '.\\MyContacts.txt', RAM = True, separator = ' | ', page_size = 10,
                           console_width = 130)
        self.config = config

        self.echo = Echo(config.style, config.style_path, config.console, config.ANSI, config.page_size, config.separator)
        self.titles = ['№', "Фамилия", "Имя", "Отчество", "Название организации", "Телефон рабочий", "Телефон личный"]
        self.table = Table(config.table_path, self.titles, True, config.RAM, config.page_size)
        self.FLAG = True
        self.sizeCols = self.table.maxLengths
        self.cancel = ['\\cancel', '\\c', '\\отмена','\\о']
        self.next = ['\\д','\\далее','\\n','\\next']
        self.back = ['\\н','\\назад','\\b','\\back']
    
    def printConacts(self)->None:
        self.echo.printTable(self.table.getAll(),self.table.maxLengths)

    def formatPhoneNumber(self, number:str)->str:
            # Удаляем все, кроме цифр и +
            number = re.sub('[^0-9+]', '', number)
            # т.к номер может быть любым к примеру +6189164(XXXX)XX-XX
            # поэтому возьмем только формат: +(код страны)(3 цифры региона)XXX-XX-XX т.е 10 цифр + код страны
            code = number[:-10] or "8"# Если номер был (ххх)ххх-хх-хх дописываем 8 что внутри страны
            
            number = number[-10:]
            # проверем длину номера и кода
            if  len(number)== 10 and number.isdecimal() and ( code.startswith("+") and 1<len(code)<9 or code == '8'):#
                # Форматируем строку
                formatted_phone_number = '{}({})-{}-{}-{}'.format(
                                    code,
                                    number[:3],
                                    number[3:6],
                                    number[6:8],
                                    number[8:]
                                        )
                # корректные вырианты : +7(XXX)XXX-XX-XX, 8(XXX)XXX-XX-XX,'+1234567(XXX)-XXX-XX-XX', (XXX)XXX-XX-XX
                return formatted_phone_number
            # не корректные вырианты : 7(XXX)XXX-XX-XX, 8(XXXX)XXX-XX-XX,(XXXX)XXX-XX-XX,', +(XXX)XXX-XX-XX, +12345678(XXX)-XXX-XX-XX'
            return ''
        
    def addContact(self)->None:
        contact_info = []
        for title in self.titles[1:4]:
            inp = input(f"{title}: ")
            if inp.lower() in self.cancel:
                self.echo.printErr('Контакт не обновлен')
                return
            contact_info.append(inp.strip().capitalize() )

        company = input("Название организации: ").strip()
        if company.lower() in self.cancel:
            self.echo.printErr('Контакт не обновлен')
            return
        contact_info.append(company)
        
        work_num = ''
        while not work_num:
            input_num = input("Введите рабочий телефон: ").lower()
            work_num = self.formatPhoneNumber(input_num)
            if input_num in self.cancel:
                self.echo.printErr('Контакт не добавлен')
                return
        contact_info.append(work_num)
        person_num = ''
        while not person_num:
            input_num = input("Введите личный телефон: ").lower()
            person_num = self.formatPhoneNumber(input_num)
            if input_num in self.cancel:
                self.echo.printErr('Контакт не добавлен')
                return
        contact_info.append(person_num)
        result = self.table.addLine(contact_info)
        if result:
            self.echo.printInfo('Контакт добавлен')
        else:
            self.echo.printErr('Контакт не добавлен')

    def updateContact(self)->None:
        search_id = ''
        while not search_id.isdecimal():
            search_id = input("Введите номер строки: ").strip()
            if search_id in self.cancel:
                self.echo.printErr('Контакт не обновлен')
                return
        search_id = int(search_id)
        search_list = self.table.searchID(search_id)
        if search_list[1:]:
            self.echo.printTable(search_list, self.sizeCols)
            update_list = []
            for title in self.titles[1:4]:
                if title.lower() in self.cancel:
                    self.echo.printErr('Контакт не обновлен')
                    return
                update_list.append(input(f"{title}: ").strip().capitalize() )
                
            company = input("Название организации: ").strip()
            if company.lower() in self.cancel:
                self.echo.printErr('Контакт не обновлен')
                return
            update_list.append(company)
            
            work_num=''
            while not work_num:
                input_num = input("Введите рабочий телефон: ").lower()
                work_num = self.formatPhoneNumber(input_num)
                if input_num in self.cancel:
                    self.echo.printErr('Контакт не обновлен')
                    return
            update_list.append(work_num)
            
            person_num = ''
            while not person_num:
                input_num = input("Введите личный телефон: ").lower()
                person_num = self.formatPhoneNumber(input_num)
                if input_num in self.cancel:
                    self.echo.printErr('Контакт не добавлен')
                    return
            update_list.append(person_num)
            result = self.table.updateLine(search_id, update_list)
            if result:
                self.echo.printInfo('Контакт обновлен')
            else:
                self.echo.printErr('Контакт не обновлен')
        else:
            self.echo.printErr('Строка не найдена')
                    

    
    def searchKeys(self)->None:
        keys = input('Введите ключевые слова через ",": ')
        if keys.lower() in self.cancel:
            return None
        list_keys = [key.strip() for key in keys.split(',')]
        result = self.table.searchKey(list_keys)
        if result:
            self.echo.printTable(result, self.sizeCols)
        else:
            self.echo.printErr('Совпадения не найдены')

    def searchMath(self)->None:
        string = input('Поиск: ')
        if string.lower() in self.cancel:
            return None
        result = self.table.searchMath(string)
        if not result:
            self.echo.printErr('Совпадения не найдены')
            return None
        self.echo.printTable(result, self.sizeCols)

    def pageContacts(self):
        page = self.table.getPage()
        self.echo.printTable(page, self.sizeCols)
        info = 'Введите номер страницы, "\\д" для следующей страницы, "\\н" для предыдущей страницы или "\\о" для отмены'
        self.echo.printInfo(info)
        while True:
            comand = input('>>').strip().lower()
            if comand.isdecimal():
                self.table.updatePage( int(comand) )
            elif comand in self.next:
                self.table.nextPage()
            elif comand in self.back:
                self.table.backPage()
            elif comand in self.cancel:
                break
            else:
                self.echo.printInfo(info)
                continue
            page = self.table.getPage()
            self.echo.printTable(page, self.sizeCols)
              
    def setting(self):
        self.echo.printInfo('В разработке...')
        
    def help(self)->None:
        self.echo.printInfo(" 1. 'Все контакты' отображает все контакты из справочника")
        self.echo.printInfo(" 2. 'Открыть страницу' отображает контакты из справочника постранично")
        self.echo.printInfo(" 3. 'Добавить контакт' позволяет добавить контакт в сравочник")
        self.echo.printInfo(" 4. 'Редактировать контакт' позволяет изменить контакт в сравочник")
        self.echo.printInfo(" 5. 'Поиск по ключевым словам' позволяет найти контакт в сравочнике по ключевым словам (Зависим от регистра)")
        self.echo.printInfo(" 6. 'Поиск по совпадению' позволяет найти контакт в сравочнике по совпадению (Независим от регистра)")
        self.echo.printInfo(" 9. Выход")
        self.echo.printInfo("Команды для отмены действия:  " + ', '.join(self.cancel))
        
    def stop(self):
        self.FLAG = False

        
    def start(self):
        hello = '''                           ___            _             _       
                          / __\___  _ __ | |_ __ _  ___| |_ ___ 
                         / /  / _ \| '_ \\| __/ _` |/ __| __/ __|
                        / /__| (_) | | | | || (_| | (__| |_\\__ \\
                        \____/\\___/|_| |_|\\__\\__,_|\\___|\\__|___/
                    '''

        self.echo.printErr(hello)

        self.echo.printInfo(" 1. Все контакты")
        self.echo.printInfo(" 2. Открыть страницу")
        self.echo.printInfo(" 3. Добавить контакт")
        self.echo.printInfo(" 4. Редактирование записи")
        self.echo.printInfo(" 5. Поиск по ключевым словам")
        self.echo.printInfo(" 6. Поиск по совпадению")
        self.echo.printInfo(" 7. Настройки")
        self.echo.printInfo(" 8. Помощь")
        self.echo.printInfo(" 9. Выход")
        
        while self.FLAG:

            command = input(">>")
            if command == "1":
                self.printConacts()
            elif command == "2":
                self.pageContacts()
            elif command == "3":
                self.addContact()
            elif command == "4":
                self.updateContact()
            elif command == "5":
                self.searchKeys()
            elif command == '6':
                self.searchMath()
            elif command == '7':
                self.setting()
            elif command == '8':
                self.help()
            elif command == "9":
                self.stop()


if __name__ == "__main__":

    Contacts = Contacts('.\\config\\config.json')
    Contacts.start()







    

