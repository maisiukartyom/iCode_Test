from pymongo import IndexModel, ASCENDING
from datetime import datetime
from db import connect_to_db


class Project:
    def __init__(self, name):
        self.name = name
        self.creation_date = datetime.utcnow()
        self.contracts = []
        self.active_contract = None


class Contract:
    def __init__(self, name):
        self.name = name
        self.creation_date = datetime.utcnow()
        self.signing_date = None
        self.status = 'черновик'
        self.project = None

    def confirm(self):
        if self.status == 'черновик':
            self.status = 'активен'
            self.signing_date = datetime.utcnow()

    def finish(self):
        if self.status == 'активен':
            self.status = 'завершен'


class ProjectManager:
    def __init__(self, db):
        self.db = db
        self.projects = db['projects']

        # Создаем уникальный индекс для поля 'name' в коллекции 'projects'
        projects_index = IndexModel([('name', ASCENDING)], unique=True)
        self.projects.create_indexes([projects_index])

    def create_project(self, name):
        try:
            project = Project(name)
            self.projects.insert_one(project.__dict__)
            print('Проект успешно создан!')
        except:
            print("Проект с таким названием уже существует!")

    def add_contract_to_project(self, project_name, contract_name):
        project = self.projects.find_one({'name': project_name})
        if not project:
            print("Проект не найден.")
            return

        contract = self.db['contracts'].find_one({'name': contract_name})
        if not contract:
            print("Договор не найден.")
            return

        if contract['status'] != 'активен':
            print("Нельзя добавить неактивный договор в проект.")
            return

        if project.get('active_contract'):
            print("В проекте уже есть активный договор.")
            return

        if contract.get('project'):
            print("Договор уже добавлен в другой проект.")
            return

        contract['project'] = project['name']
        self.db['contracts'].replace_one({'name': contract['name']}, contract)

        self.projects.update_one({'name': project_name}, {'$set': {'active_contract': contract_name}})
        self.projects.update_one({'name': project_name}, {'$push': {'contracts': contract_name}})

        print("Контракт успешно добавлен!")

    def finish_contract(self, project_name, contract_name):
        project = self.projects.find_one({'name': project_name})
        if not project:
            print("Проект не найден.")
            return

        contract = self.db['contracts'].find_one({'name': contract_name})
        if not contract:
            print("Договор не найден.")
            return

        if contract.get('project') != project['name']:
            print("Договор не принадлежит указанному проекту.")
            return

        if contract['status'] == 'завершен':
            print('Данный контракт уже завершён!')
        else:
            contract['status'] = 'завершен'
            self.db['contracts'].replace_one({'name': contract_name}, contract)
            self.projects.update_one({'name': project_name}, {'$set': {'active_contract': None}})
            print('Контракт успешно завершён!')

    def list_projects(self):
        return list(self.projects.find())


class ContractManager:
    def __init__(self, db):
        self.db = db
        self.contracts = db['contracts']

        # Создаем уникальный индекс для поля 'name' в коллекции 'contracts'
        contracts_index = IndexModel([('name', ASCENDING)], unique=True)
        self.contracts.create_indexes([contracts_index])

    def create_contract(self, name):
        try:
            contract = Contract(name)
            self.contracts.insert_one(contract.__dict__)
            print("Договор успешно создан!")
        except:
            print("Договор с таким названием уже существует!")

    def confirm_contract(self, contract_name):
        contract = self.contracts.find_one({'name': contract_name})

        if not contract:
            print("Договор не найден.")
            return

        if contract['status'] == 'черновик':
            contract['status'] = 'активен'
            contract['signing_date'] = datetime.utcnow()
            self.contracts.replace_one({'name': contract_name}, contract)
            print('Договор активен!')
        elif contract['status'] == 'активен':
            print("Договор уже активен!")
        else:
            print("Нельзя активировать завершённый договор!")

    def finish_contract(self, contract_name):
        contract = self.contracts.find_one({'name': contract_name})

        if not contract:
            print("Договор не найден.")
            return

        if contract['status'] == 'активен':
            contract['status'] = 'завершен'
            self.contracts.replace_one({'name': contract_name}, contract)
            if contract['project'] is not None:
                self.db['projects'].update_one({'name': contract['project']}, {'$set': {'active_contract': None}})

            print('Договор завершён!')
        elif contract['status'] == 'черновик':
            print('Договор ещё черновик!')
        else:
            print('Договор уже завершён!')

    def list_contracts(self):
        return list(self.contracts.find())


if __name__ == '__main__':
    client = connect_to_db()

    db = client['contracts_db']

    project_manager = ProjectManager(db)
    contract_manager = ContractManager(db)

    while True:
        print("Выберите действие:")
        print("1. Проект")
        print("2. Договор")
        print("3. Просмотреть список проектов")
        print("4. Просмотреть список договоров")
        print("5. Завершить работу с программой")
        choice = input("Введите номер действия: ")

        if choice == '1':
            print("1. Создать проект")
            print("2. Добавить договор к проекту")
            print("3. Завершить договор в проекте")
            print("4. Вернуться")
            sub_choice = input("Введите номер действия: ")

            if sub_choice == '1':
                name = input("Введите название проекта: ")
                project_manager.create_project(name)
            elif sub_choice == '2':
                project_id = input("Введите название проекта: ")
                contract_id = input("Введите название договора: ")
                project_manager.add_contract_to_project(project_id, contract_id)
            elif sub_choice == '3':
                project_id = input("Введите название проекта: ")
                contract_id = input("Введите название договора: ")
                project_manager.finish_contract(project_id, contract_id)
            elif sub_choice == '4':
                continue
            else:
                print("Некорректный выбор.")
        elif choice == '2':
            print("1. Создать договор")
            print("2. Подтвердить договор")
            print("3. Завершить договор")
            print("4. Вернуться")

            sub_choice = input("Введите номер действия: ")

            if sub_choice == '1':
                name = input("Введите название договора: ")
                contract_manager.create_contract(name)
            elif sub_choice == '2':
                contract_id = input("Введите название договора: ")
                contract_manager.confirm_contract(contract_id)
            elif sub_choice == '3':
                contract_id = input("Введите название договора: ")
                contract_manager.finish_contract(contract_id)
            elif sub_choice == '4':
                continue
            else:
                print("Некорректный выбор.")
        elif choice == '3':
            projects = project_manager.list_projects()

            if projects:
                count = 1
                for project in projects:
                    print(f"{count}) ID: {project['_id']}, Название: {project['name']}, Контракты: {project['contracts']}"
                          f", Активный контракт: {project['active_contract']}")
                    count += 1
            else:
                print("Список проектов пуст.")
        elif choice == '4':
            contracts = contract_manager.list_contracts()
            if contracts:
                count = 1
                for contract in contracts:
                    print(f"{count}) ID: {contract['_id']}, Название: {contract['name']}, Статус: {contract['status']},"
                          f" Проект: {contract['project']}")
                    count += 1
            else:
                print("Список договоров пуст.")
        elif choice == '5':
            break
        else:
            print("Некорректный выбор.")

        print("Enter...")
        input()
        