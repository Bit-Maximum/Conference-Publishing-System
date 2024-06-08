from django.core.management.base import BaseCommand
from ...models import CustomUser, AuthorInfo, ArticleInfo, Section, SectionEditor, Comment, Source


class Command(BaseCommand):
    help = 'Create fake data for testing'

    def handle(self, *args, **options):
        data = {
            "users": [
                {
                    "email": "lena@mail.com",
                    "password": "1234",
                    "last_name": "Кобыльцова",
                    "first_name": "Елена",
                    "middle_name": "Эдуардовна"
                },
                {
                    "email": "max@mail.com",
                    "password": "1234",
                    "last_name": "Меркурьев",
                    "first_name": "Максим",
                    "middle_name": "Алексеевич"
                },
                {
                    "email": "anton@mail.com",
                    "password": "1234",
                    "last_name": "Шаповал",
                    "first_name": "Антон",
                    "middle_name": "Сергеевич"
                },
                {
                    "email": "jena@mail.com",
                    "password": "1234",
                    "last_name": "Кильгановская",
                    "first_name": "Евгения",
                    "middle_name": "Ростиславовна"
                },
                {
                    "email": "arina@mail.com",
                    "password": "1234",
                    "last_name": "Савушкина",
                    "first_name": "Арина",
                    "middle_name": "Андреевна"
                }
            ],
            "authors": [
                {
                    "first_name_translation": "Elena",
                    "last_name_translation": "Kobyltsova",
                    "major": "Издательское дело",
                    "level": "Бакалавриат",
                    "course": 4
                },
                {
                    "first_name_translation": "Maxim",
                    "last_name_translation": "Merkurev",
                    "major": "Издательское дело",
                    "level": "Бакалавриат",
                    "course": 4
                },
                {
                    "first_name_translation": "Anton",
                    "last_name_translation": "Shapoval",
                    "major": "Журналистика",
                    "level": "Бакалавриат",
                    "course": 3
                },
                {
                    "first_name_translation": "Evgenia",
                    "last_name_translation": "Kilganovskaya",
                    "major": "Реклама и связь с общественостью",
                    "level": "Бакалавриат",
                    "course": 2
                },
                {
                    "first_name_translation": "Arina",
                    "last_name_translation": "Savushkina",
                    "major": "Издательское дело",
                    "level": "Бакалавриат",
                    "course": 4
                }
            ],
            "editors_users": [
                {
                    "email": "staff@mail.com",
                    "password": "1234",
                    "last_name": "Баринова",
                    "first_name": "Ксения",
                    "middle_name": "Владимировна"
                },
                {
                    "email": "staff2@mail.com",
                    "password": "1234",
                    "last_name": "Костина",
                    "first_name": "Екатерина",
                    "middle_name": "Юрьевна"
                }
            ],
            "article_good":
                {
                    "adviser_last_name": "Баринова",
                    "adviser_first_name": "Ксения",
                    "adviser_middle_name": "Владимировна",
                    "adviser_last_name_translation": "Barinova",
                    "adviser_first_name_translation": "Ksenia",
                    "adviser_degree": "кандидат филологических наук",

                    "title": "Актуальные практики книгораспространения на Дальнем Востоке",
                    "title_translation": "Current book distribution practices in the Far East",
                    "abstract": "В рамках 23-й Дальневосточной выставки-ярмарки «Печатный двор – 2022» был проведён опрос восьми издательств и двух книжных магазинов. В выборку попали организации из пяти регионов ДФО. Исследование показало, что в густонаселённых регионах Дальнего Востока доминируют способы распространения «через интернет», в то время как в малонаселённых более эффективны способы, связанные с организацией досуга для потенциального покупателя. Выявлено, что пандемия коронавируса не оказала значимого влияния на работу большинства издательств и книжных магазинов Дальнего Востока. А введение санкций против России в 2022 г. привело к потере части аудитории организаций, сокращению тиражей и повышению цен на продукцию.",
                    "abstract_translation": "As part of the 23rd Far Eastern exhibition-fair «Pechatnyy dvor – 2022», a survey was conducted of eight publishing houses and two bookstores. The sample included organizations from five regions of the Far Eastern Federal District. The study showed that in relatively populous regions of the Far East, distribution «Internet» methods dominate, while in sparsely populated regions, methods related to organizing leisure for a potential buyer are more effective. It was revealed that the coronavirus pandemic did not have a significant impact on the work of most publishing houses and bookstores in the Far East. And the imposition of sanctions against Russia in 2022 led to the loss of a part of the audience of organizations, a reduction in circulation and an increase in product prices.",
                    "keywords": "книгораспространение, издательство, книжный магазин, издательский бизнес, книжная культура",
                    "keywords_translation": "book distribution, publishing house, bookstore, publishing business, book culture"
                },
            "article_bad":
                {
                    "title": "Цифровая трансформация: как сеть ресторанов быстрого питания стала лидером на рынке благодаря цифровым технологиям",
                    "title_translation": "Digital transformation: how a fast food restaurant chain became a market leader thanks to digital technologies",
                    "abstract": "Настоящее исследование представляет собой анализ истории успеха компании Додо Пицца, быстро растущей международной сети ресторанов быстрого питания, запущенной в России в 2011 году предпринимателем Федором Овчинниковым. Умело используя цифровые технологии, Ф. Овчинников смог развить небольшую компанию по приготовлению пиццы до одной из крупнейших сетей фастфуда в России. За период 2011-2021 гг. лет его компания достигла выручки в 500 миллионов долларов США в год и в настоящее время продолжает завоевывать мировой рынок, активно расширяясь на международной арене.",
                    "abstract_translation": "This study is an analysis of the success story of Dodo Pizza, a rapidly growing international fast food restaurant chain launched in Russia in 2011 by entrepreneur Fyodor Ovchinnikov. By skillfully using digital technologies, F. Ovchinnikov was able to develop a small pizza company into one of the largest fast food chains in Russia. For the period 2011-2021 Over the years, his company has reached revenues of US$500 million per year and currently continues to conquer the global market, actively expanding internationally.",
                    "keywords": "цифровая трансформация, цифровые технологии, инвестиционная деятельность",
                    "keywords_translation": "digital transformation, digital technologies, investment activities"
                },
            "comments": [
                {
                    "content": """Здравствуйте!\n
\n
Ваша статья возвращена рецензентом на доработку.\n
Замечания рецензента и редколлегии см. ниже, а также в тексте прикрепленной статьи (желтый маркер — пометы рецензента, примечания от редколлегии).\n
 \n
Статья нуждается в тщательной вычитке (устранить опечатки, перестроить грамматические конструкции) и стилистической правке. Ряд правок внесены рецензентом, случаи опечаток, стилистических погрешностей отмечены желтым маркером в тексте статьи.
Аннотация (и ее перевод соответственно) требует корректировки: «На основе контент-анализа их сайтов и аккаунтов в социальных сетях выявляется региональная специфика приморских магазинов комиксов». При этом в статье рассматривается один приморский книжный магазин комиксов.
Необходимо сформулировать выводы более конкретно.\n
 \n
Вам необходимо в срок до 29 мая выслать ответным письмом исправленный вариант статьи.""",
                },
                {
                    "content": "Статья принята к публикации."
                }
            ],
            "sources": [
                {
                    "content": "Авдеева, Н. В. Структурирование научной статьи в формате «Introduction, Methods, Results and Discussion» : что важно учитывать начинающему автору / Н. В. Авдеева, Г. А. Лобанова // Открытое образование. — 2016. — Т. 20. — № 5. — С. 4–10."
                },
                {
                    "content": "Мильчин, А. Э. Справочник издателя и автора / А. Э. Мильчин, Л. К. Чельцова. — Изд. 5-е. — Москва : Студия Артемия Лебедева, 2018. — 1010 с."
                }
            ]
        }

        author_users = []
        author_authors_info = []

        editor_users = []
        editor_editors_info = []

        CustomUser.objects.create_superuser(
            email='admin@mail.com',
            password='1234',
            last_name='Белевщук',
            first_name='Гилина',
            middle_name='Павловна'
        )
        print("Superuser created")

        for user in data.get("users"):
            new_user = CustomUser.objects.create_user(
                email=user.get('email'),
                password=user.get('password'),
                last_name=user.get('last_name'),
                first_name=user.get('first_name'),
                middle_name=user.get('middle_name')
            )
            author_users.append(new_user)
        print("Users created")

        for i in range(len(data.get("authors"))):
            author = data.get("authors")[i]
            new_user = AuthorInfo.objects.create(
                user=author_users[i],
                first_name_translation=author.get('first_name_translation'),
                last_name_translation=author.get('last_name_translation'),
                major=author.get('major'),
                level=author.get('level'),
                course=author.get('course')
            )
            author_authors_info.append(new_user)
        print("Authors created")

        for user in data.get("editors_users"):
            new_user = CustomUser.objects.create_user(
                email=user.get('email'),
                password=user.get('password'),
                last_name=user.get('last_name'),
                first_name=user.get('first_name'),
                middle_name=user.get('middle_name'),
                is_staff=True
            )
            editor_users.append(new_user)
        print("Editors_users created")

        for i in range(len(data.get("editors_users"))):
            editor = data.get("editors_users")[i]
            new_editor = SectionEditor.objects.create(
                user=editor_users[i],
                section=Section.objects.get(pk=i + 1),
                confirmed=True
            )
            editor_editors_info.append(new_editor)
        print("Editors created")

        art = data.get("article_good")
        article_good = ArticleInfo.objects.create(
            section=Section.objects.get(id=1),
            title=art.get("title"),
            title_translation=art.get("title_translation"),
            abstract=art.get("abstract"),
            abstract_translation=art.get("abstract_translation"),
            keywords=art.get("keywords"),
            keywords_translation=art.get("keywords_translation"),
            adviser_first_name=art.get("adviser_first_name"),
            adviser_last_name=art.get("adviser_last_name"),
            adviser_middle_name=art.get("adviser_middle_name"),
            adviser_first_name_translation=art.get("adviser_first_name_translation"),
            adviser_last_name_translation=art.get("adviser_last_name_translation"),
            adviser_degree=art.get("adviser_degree")
        )
        article_good.authors.add(*author_users[0:3])
        print("Article 'good' created")

        art = data.get("article_bad")
        article_bad = ArticleInfo.objects.create(
            section=Section.objects.get(id=1),
            title=art.get("title"),
            title_translation=art.get("title_translation"),
            abstract=art.get("abstract"),
            abstract_translation=art.get("abstract_translation"),
            keywords=art.get("keywords"),
            keywords_translation=art.get("keywords_translation"),
        )
        article_bad.authors.add(*author_users[3:6])
        print("Article 'bad' created")

        for comment in data.get("comments"):
            Comment.objects.create(
                article=article_good,
                editor=editor_editors_info[0],
                content=comment.get("content")
            )
        print("Comments created")

        for source in data.get("sources"):
            Source.objects.create(
                article=article_good,
                content=source.get("content")
            )
        print("Sources created")

        print("Successful creation of fake data")
