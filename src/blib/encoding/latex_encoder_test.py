from unittest import TestCase

from blib.encoding import LatexEncoder


class TestLatexEncoder(TestCase):
    def test_encoding(self):

        cases = [
            (r"Studies of α-Fe2O3", r"{Studies} of $\alpha$-{Fe}$_{2}${O}$_{3}$"),
            (r"Studies of α-Fe<sub>2</sub>O<sub>3</sub>", r"{Studies} of $\alpha$-{Fe}$_{2}${O}$_{3}$"),
            (r'Studies of α-<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mrow><mml:msub><mml:mi>Fe</mml:mi><mml:mn>2</mml:mn></mml:msub><mml:msub><mml:mi>O</mml:mi><mml:mn>3</mml:mn></mml:msub></mml:mrow></mml:math>', r"{Studies} of $\alpha$-${Fe}_{2}{O}_{3}$"),
            (r'Theory of the Role of Covalence Fe3O4 in the Perovskite-Type Manganites<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML" display="inline"><mml:mo>[</mml:mo><mml:mi mathvariant="normal">La</mml:mi><mml:mo>,</mml:mo><mml:mi> </mml:mi><mml:mi>M</mml:mi><mml:mo>(</mml:mo><mml:mi mathvariant="normal">II</mml:mi><mml:mo>)</mml:mo><mml:mo>]</mml:mo><mml:mi mathvariant="normal">Mn</mml:mi><mml:mrow><mml:msub><mml:mrow><mml:mi mathvariant="normal">O</mml:mi></mml:mrow><mml:mrow><mml:mn>3</mml:mn></mml:mrow></mml:msub></mml:mrow></mml:math>',
             r'{Theory} of the {Role} of {Covalence} {Fe}$_{3}${O}$_{4}$ in the {Perovskite}-{Type} {Manganites}$[\mathrm{La}, M(\mathrm{II})]\mathrm{Mn}{\mathrm{O}}_{3}$'),
            # (r'Quasi-two-dimensional ferromagnetism and anisotropic interlayer couplings in the magnetic topological insulator <mml:math xmlns:mml="http://www.w3.org/1998/{Math}/{MathML}"><mml:mrow><mml:msub><mml:mi>MnBi</mml:mi><mml:mn>2</mml:mn></mml:msub><mml:msub><mml:mi>Te</mml:mi><mml:mn>4</mml:mn></mml:msub></mml:mrow></mml:math>',
            #  r'{Quasi}-two-dimensional ferromagnetism and anisotropic interlayer couplings in the magnetic topological insulator $MnBi_{2}Te_{4}$')
        ]

        encoder = LatexEncoder()

        for test_text, expected_result in cases:
            self.assertEqual(expected_result, encoder.encode(test_text))

    def test_mathml(self):
        cases = [
            (r'<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mrow><mml:mi>E</mml:mi><mml:mo>=</mml:mo><mml:mi>m</mml:mi><mml:msup><mml:mi>c</mml:mi><mml:mn>2</mml:mn></mml:msup></mml:mrow></mml:math>', r"$E=m{c}^{2}$"),
            (r'<mml:math xmlns:mml="http://www.w3.org/1998/Math/MathML"><mml:mrow><mml:msub><mml:mi>Fe</mml:mi><mml:mn>2</mml:mn></mml:msub><mml:msub><mml:mi>O</mml:mi><mml:mn>3</mml:mn></mml:msub></mml:mrow></mml:math>', r"${Fe}_{2}{O}_{3}$"),
        ]

        encoder = LatexEncoder()

        for test_text, expected_result in cases:
            self.assertEqual(expected_result, encoder.encode(test_text))


