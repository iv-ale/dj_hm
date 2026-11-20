from django.test import TestCase, override_settings


class ShopPagesTests(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Это учебный сайт-магазин")

    def test_about_page(self):
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "О проекте")

    def test_contacts_page(self):
        response = self.client.get("/contacts/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student@example.com")

    def test_hello_page(self):
        response = self.client.get("/hello/Эмиль/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Привет, Эмиль!")

    def test_hello_escapes_html(self):
        response = self.client.get("/hello/%3Cb%3E/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<b>")
        self.assertContains(response, "&lt;b&gt;")

    def test_calc_page(self):
        response = self.client.get("/calc/7/3/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "10")
        self.assertContains(response, "4")
        self.assertContains(response, "21")

    def test_calc_rejects_non_numbers(self):
        response = self.client.get("/calc/seven/3/")
        self.assertEqual(response.status_code, 404)


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class Custom404Tests(TestCase):
    def test_missing_page_uses_custom_template(self):
        response = self.client.get("/no-such-page/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Такой страницы нет", status_code=404)
        self.assertContains(response, 'href="/"', status_code=404)
