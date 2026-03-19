from unittest import TestCase

from blib.encoding.unicode_encoder import UnicodeEncoder


class TestUnicodeMathmlEncoder(TestCase):
    def test_inline_mathml_is_encoded_without_latex_helpers(self):
        text = (
            'Magnetic properties of<i>R</i>ions in<i>R</i>'
            '<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline">'
            '<mml:mrow><mml:msub><mml:mrow><mml:mi mathvariant="normal">Co</mml:mi></mml:mrow>'
            '<mml:mrow><mml:mn>5</mml:mn></mml:mrow></mml:msub></mml:mrow></mml:math>'
            'compounds'
        )

        self.assertEqual(
            UnicodeEncoder().encode(text),
            'Magnetic properties ofRions inR Co₅ compounds',
        )
