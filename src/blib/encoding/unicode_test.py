from unittest import TestCase

from .unicode_encoder import UnicodeEncoder


class TestUnicodeEncoder(TestCase):
    def test_encoding(self):

        cases = [
            (r"Studies of α-Fe2O3", r"Studies of α-Fe₂O₃"),
            (r"Studies of α-Fe<sub>2</sub>O<sub>3</sub>", r"Studies of α-Fe₂O₃"),
            # (r'Quasi-two-dimensional ferromagnetism and anisotropic interlayer couplings in the magnetic topological insulator <mml:math xmlns:mml="http://www.w3.org/1998/{Math}/{MathML}"><mml:mrow><mml:msub><mml:mi>MnBi</mml:mi><mml:mn>2</mml:mn></mml:msub><mml:msub><mml:mi>Te</mml:mi><mml:mn>4</mml:mn></mml:msub></mml:mrow></mml:math>',
            #  r'{Quasi}-two-dimensional ferromagnetism and anisotropic interlayer couplings in the magnetic topological insulator $MnBi_{2}Te_{4}$')
        ]

        encoder = UnicodeEncoder()

        for test_text, expected_result in cases:
            self.assertEqual(expected_result, encoder.encode(test_text))

