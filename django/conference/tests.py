from django.test import TestCase
from django.contrib.auth import get_user_model

from . models import AuthorInfo, ScienceDegree, AdviserInfo, Section, SectionEditor, ArticleInfo, ArticleText, Comment


class UsersManagersTests(TestCase):
    def test_create_user(self):

        User = get_user_model()
        user = User.objects.create_user(email="normal@user.com", password="1234")
        self.assertEqual(user.email, "normal@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        try:
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(user.username)
        except AttributeError:
            pass
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="1234")

    def test_create_staff_user(self):
        User = get_user_model()
        staff_user = User.objects.create_staff_user(email="staff@user.com", password="1234")
        self.assertEqual(staff_user.email, "staff@user.com")
        self.assertTrue(staff_user.is_active)
        self.assertTrue(staff_user.is_staff)
        self.assertFalse(staff_user.is_superuser)
        try:
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(staff_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="staff@user.com", password="1234", is_staff=False)

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(email="super@user.com", password="foo")
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        try:
            # username does not exist for the AbstractBaseUser option
            self.assertIsNone(admin_user.username)
        except AttributeError:
            pass
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="super@user.com", password="foo", is_superuser=False)


# class ConferenceTestCase(TestCase):
#
#     def setUp(self):
#         user1 = User.objects.create_user(username="user1", password="1234", email="user1@mail.com",
#                                          first_name="Имя", middle_name="Отчество", last_name="Фамилия")
#         user2 = User.objects.create_user(username="user2", password="1234", email="user2@mail.com",
#                                          first_name="Имя", middle_name="Отчество", last_name="Фамилия")
#         user3 = User.objects.create_user(username="user3", password="1234", email="user3@mail.com",
#                                          first_name="Имя", middle_name="Отчество", last_name="Фамилия")
#         user4 = User.objects.create_user(username="user4", password="1234", email="user4@mail.com",
#                                          first_name="Имя", middle_name="Отчество", last_name="Фамилия")
#
#         correct_author = AuthorInfo.objects.create(
#             user_id=user1,
#             first_name_translation="{Author's first name}",
#             last_name_translation="{Author's last name}",
#             country="Россия",
#             city="Владивосток",
#             institution="Дальновосточный федеральный университет",
#             department="Школа исскуств и гуманитарных наук",
#             major="Журналистика",
#             level="Б",
#             course=1
#         )
#
#         wrong_author = AuthorInfo.objects.create(
#             user_id=user2,
#             first_name_translation="{Author's first name}",
#             last_name_translation="{Author's last name}",
#             country="Россия",
#             city="Владивосток",
#             institution="Дальновосточный федеральный университет",
#             department="Школа исскуств и гуманитарных наук",
#             major="Журналистика",
#             level="Г",
#             course=10
#         )
#
#         degree = ScienceDegree.objects.create(
#             short="к.ф.н.",
#             full="кандидат филологических наук"
#         )
#
#         adviser = AdviserInfo.objects.create(
#             user_id=user3,
#             degree=degree,
#             first_name="{Имя Научного Руководителя}",
#             middle_name="{Отчество Научного Руководителя}",
#             last_name="{Фамилия Научного Руководителя}",
#             first_name_translation="{Adviser's first name}",
#             last_name_translation="{Adviser's last name}"
#         )
#
#         section = Section.objects.create(
#             name="Актуальные проблемы лингвистики"
#         )
#
#         editor = SectionEditor.objects.create(
#             user_id=user4,
#             section_id=section
#         )
#
#         correct_article = ArticleInfo.objects.create(
#             author_id=correct_author,
#             section_id=section,
#             adviser_id=adviser,
#             title="{Название статьи}",
#             title_translation="{Article's title}",
#             abstract="{Аннотация статьи}",
#             abstract_translation="{Article's abstract}",
#             keywords="Журналистика, книгоиздания, филология",
#             keywords_translation="Jurnal, bookselling, philosophy"
#         )
#
#         wrong_article = ArticleInfo.objects.create(
#             author_id=correct_author,
#             section_id=section,
#             adviser_id=adviser,
#             title="{Название статьи}",
#             title_translation="{Article's title}",
#             abstract="poerokmgerml;ekm;blr;lsbk;ltknb;lsklkmlk;jhljygtfiuytvjhvywvievwkvkgvkgvkhgvkhgwvkhegvfkhevrkhgvkegvkhegvkvgeljrvhglervlegvrlegvgljervhljevrljgevghrvlebkjrngieuhrierpei irh epiugheprhgperuhgperu hperh gperh gper gherip ere;grehpgu hipruegprg herpg hepi rhrpigheprghprieghepri hgprehg perhgperhgperuhgpepgreugrperngkrjneiurgerjgnre;guephrgephredjngrnrnrerjkeg;krjjeg;rjekgljre;lkgjreig;jreg;ljre;lgknerl;ng;rlnlelgjer[oigjrelgkjr'glerjgrlkemrlke;roigje[roigjerlkgjer;lgkjroiej[goier[gnere gewurg 3g o 3ofg oue wjhbfd  jhbs ljfb sljhb lejhbglsk dflshgr",
#             abstract_translation="{Article's abstract}",
#             keywords="Журналистика, книгоиздания, филология",
#             keywords_translation="Jurnal,, ,, philosophy"
#         )
#
#         comment = Comment.objects.create(
#             article_id=correct_article,
#             editor_id=editor,
#             content="Текст комментария"
#         )
#
#     def test_correct_author(self):
#         self.assertTrue(self.correct_author)
#
#     def test_wrong_author(self):
#         self.assertFalse(self.wrong_author)
#
#     def test_correct_article(self):
#         self.assertTrue(self.correct_article)
#
#     def test_wrong_article(self):
#         self.assertFalse(self.wrong_article)


