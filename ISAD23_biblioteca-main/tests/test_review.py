from . import BaseTestClass
from bs4 import BeautifulSoup


class TestReviews(BaseTestClass):

    def test_1_get_reviews(self):
        self.login('james@gmail.com', '123456')
        response = self.client.get(f'/read-reviews?bookId=20')
        self.assertEqual(response.status_code, 200)

    def test_2_add_review(self):
        # Login the user
        login_response = self.client.post('/login', data={
            'email': 'james@gmail.com',
            'password': '123456'
        }, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200, 'Login failed')

        response = self.client.post('/post-review', json={
            'book_id': '10',
            'user_email': 'james@gmail.com',
            'rating': 5,
            'review_text': '<<ERRESEINA TEST>>',
            'title': 'Titulu adibidea'
        })

        self.assertIn('token', ''.join(response.headers.values()))
        response = self.client.get(f'/read-reviews?bookId=10')
        soup = BeautifulSoup(response.data, 'html.parser')
        reviews = soup.find_all('div', class_='card-body')
        self.assertGreater(len(reviews), 0)


    def test_3_edit_review(self):
        # Login the user
        login_response = self.client.post('/login', data={
            'email': 'james@gmail.com',
            'password': '123456'
        }, follow_redirects=True)

        self.assertEqual(login_response.status_code, 200, 'Login failed')

        # Move to the read reviews page
        response = self.client.get(f'/read-reviews?bookId=10')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        print(soup)
        enlace = soup.find('a', class_='btn btn-warning')
        import re
        review_id_match = re.search(r'reviewId=(\d+)', enlace['href'])
        if review_id_match:
            review_id = review_id_match.group(1)
            print(review_id)
        else:
            print("No se pudo encontrar 'reviewId'")

        # Edit the review
        response = self.client.post('/edit-review', json={
            'id': review_id,
            'book_id': '1',
            'user_email': 'james@gmail.com',
            'rating': 4,
            'review_text': '<<ERRESERBA EDITATUA TEST>>'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check if the review is in the database
        response = self.client.get(f'/read-reviews?bookId=1')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.data, 'html.parser')
        reviews = soup.find_all('div', class_='card-body d-flex flex-column')
        self.assertGreater(len(reviews), 0)
        found = False
        for review in reviews:
            if review.find('h5').text == 'james@gmail.com' and review.find('p',
                                                                                   class_='card-text').text == 'Test review content edited':
                found = True
        self.assertTrue(found)

