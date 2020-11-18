from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def menu():
    choice = input("1) Today's tasks\n"
                   "2) Week's tasks\n"
                   "3) All tasks\n"
                   "4) Missed tasks\n"
                   "5) Add task\n"
                   "6) Delete task\n"
                   "0) Exit\n")
    if choice == '1':
        print_task("today")
        menu()
    elif choice == '2':
        print_task("week")
        menu()
    elif choice == '3':
        print_task("all")
        menu()
    elif choice == '4':
        print_task("passed")
        menu()
    elif choice == '5':
        add_task()
        menu()
    elif choice == '6':
        delete_task()
        menu()
    elif choice == '0':
        print('Bye!')
    else:
        print('Invalid selection\n')
        menu()


def print_task(date=None):
    today = datetime.today()

    def print_rows(rows, needs_date=False):
        if len(rows) == 0:
            print('Nothing to do!')
        else:
            i = 1
            for row in rows:
                if needs_date:
                    print('{}. {}.'.format(i, row.task), row.deadline.strftime('%d %b'))
                else:
                    print('{}. {}'.format(i, row.task))
                i += 1
        print()

    if date == "today":
        print('Today', today.strftime('%d %b:'))
        rows = session.query(Table).filter(Table.deadline == today.date()).all()
        print_rows(rows)
    elif date == "week":
        for d in range(7):
            day = today + timedelta(days=d)
            print(day.strftime('%A %d %b:'))
            rows = session.query(Table).filter(Table.deadline == day.date()).all()
            print_rows(rows)
    elif date == "passed":
        print('Missed tasks:')
        rows = session.query(Table).filter(Table.deadline < today.date()).all()
        print_rows(rows, True)
    elif date == "all":
        print('All tasks:')
        rows = session.query(Table).order_by(Table.deadline).all()
        print_rows(rows, True)
    else:
        rows = session.query(Table).order_by(Table.deadline).all()
        print_rows(rows, True)


def add_task():
    print('Enter task')
    new_task = input()
    print('Enter deadline MM/DD/YYYY')
    try:
        task_deadline = datetime.strptime(input(), "%m/%d/%Y")
    except ValueError:
        print('Deadline does not match format MM/DD/YYYY\n')
        add_task()
    else:
        new_row = Table(task=new_task, deadline=task_deadline.date())
        session.add(new_row)
        session.commit()
        print('The task has been added!\n')


def delete_task():
    rows = session.query(Table).order_by(Table.deadline).all()
    if len(rows) == 0:
        print('Nothing to delete\n')
    else:
        print('Choose the number of the task you want to delete:')
        print_task()
        try:
            specific_row = rows[int(input()) - 1]
        except (IndexError, ValueError):
            print('Invalid selection\n')
            delete_task()
        else:
            session.delete(specific_row)
            session.commit()
            print('The task has been deleted!\n')


menu()
