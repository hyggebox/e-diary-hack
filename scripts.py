import argparse
import os
import random

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from datacenter.models import Chastisement, Commendation, Lesson, Mark, Schoolkid


def find_child(child_name):
    found_child = Schoolkid.objects.filter(full_name__contains=child_name).get()
    return found_child


def fix_marks(schoolkid):
    Mark.objects.filter(schoolkid=schoolkid, points__lt=4).update(points=5)


def remove_chastisements(schoolkid):
    chastisements = Chastisement.objects.filter(schoolkid=schoolkid)
    chastisements.delete()


def create_commendation(schoolkid, subject_title):
    commendations = ["Молодец!", "Отлично!", "Хорошо!",
                     "Гораздо лучше, чем я ожидал!",
                     "Ты меня приятно удивил!", "Великолепно!", "Прекрасно!",
                     "Ты меня очень обрадовал!",
                     "Именно этого я давно ждал от тебя!",
                     "Сказано здорово – просто и ясно!",
                     "Ты, как всегда, точен!",
                     "Очень хороший ответ!", "Талантливо!",
                     "Ты сегодня прыгнул выше головы!",
                     "Уже существенно лучше!", "Потрясающе!", "Замечательно!",
                     "Прекрасное начало!", "Так держать!",
                     "Ты на верном пути!",
                     "Здорово!", "Это как раз то, что нужно!",
                     "Я тобой горжусь!",
                     "С каждым разом у тебя получается всё лучше!",
                     "Мы с тобой не зря поработали!",
                     "Я вижу, как ты стараешься!", "Ты растешь над собой!",
                     "Ты многое сделал, я это вижу!",
                     "Теперь у тебя точно все получится!"]
    lesson = Lesson.objects.filter(year_of_study=schoolkid.year_of_study,
                                   group_letter=schoolkid.group_letter,
                                   subject__title=subject_title).order_by("-date")[0:1].get()
    if lesson:
        Commendation.objects.create(
            text=random.choice(commendations),
            created=lesson.date,
            schoolkid=schoolkid,
            subject=lesson.subject,
            teacher=lesson.teacher
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Исправляет оценки и "
                                                 "комментарии в эл.дневнике "
                                                 "для указанного ученика")
    parser.add_argument("name", nargs="?", default="Фролов Иван",
                        help="имя ученика")
    parser.add_argument("-s", "--subjects", nargs="+", type=str)
    args = parser.parse_args()

    try:
        child = find_child(args.name)
    except Schoolkid.DoesNotExist:
        print(f"Ученика с именем {args.name} нет в базе данных")
    except Schoolkid.MultipleObjectsReturned:
        print(f"Найдено несколько учеников с именем {args.name}. "
              f"Уточните полное имя")
    else:
        fix_marks(child)
        remove_chastisements(child)

        subjects = args.subjects
        if subjects:
            for subject in subjects:
                try:
                    create_commendation(child, subject.capitalize())
                except Lesson.DoesNotExist:
                    print(f"Предмета “{subject}“ у ученика {child.full_name} "
                          f"не найдено в базе")
