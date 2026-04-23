import unittest

from tools.title_validator import pluralize_keyword


class PluralizationTests(unittest.TestCase):
    def test_uncountables_and_exceptions(self):
        cases = {
            "decor": "decor",
            "home decor": "home decor",
            "jewellery": "jewellery",
            "sportswear": "sportswear",
            "software": "software",
            "series": "series",
            "species": "species",
            "information": "information",
        }
        for src, expected in cases.items():
            with self.subTest(src=src):
                self.assertEqual(pluralize_keyword(src), expected)

    def test_regular_patterns(self):
        cases = {
            "shirt": "shirts",
            "dress": "dresses",
            "glass": "glasses",
            "baby": "babies",
            "toy": "toys",
            "box": "boxes",
            "brush": "brushes",
        }
        for src, expected in cases.items():
            with self.subTest(src=src):
                self.assertEqual(pluralize_keyword(src), expected)

    def test_f_and_o_endings(self):
        cases = {
            "knife": "knives",
            "wolf": "wolves",
            "roof": "roofs",
            "hero": "heroes",
            "potato": "potatoes",
            "photo": "photos",
            "piano": "pianos",
            "video": "videos",
        }
        for src, expected in cases.items():
            with self.subTest(src=src):
                self.assertEqual(pluralize_keyword(src), expected)

    def test_keyword_phrases(self):
        cases = {
            "pink shirt": "pink shirts",
            "nike shoe": "nike shoes",
            "women dress": "women dresses",
            "kids toy": "kids toys",
            "shoe for boys": "shoes for boys",
            "watch with strap": "watches with strap",
        }
        for src, expected in cases.items():
            with self.subTest(src=src):
                self.assertEqual(pluralize_keyword(src), expected)


if __name__ == "__main__":
    unittest.main()
