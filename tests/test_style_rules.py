import unittest
from app.processor.document_processor import DocumentProcessor
from app.models.rule_schema import RuleCategory

class TestStyleRules(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor()

    def test_document_structure_rules(self):
        """Test document structure rules (sections, headings, tables)"""
        test_cases = [
            ("see synopsis for details", "see Synopsis for details"),
            ("refer to appendix A", "refer to Appendix A"),
            ("shown in table 1", "shown in Table 1"),
            ("see figure 2", "see Figure 2"),
            ("in materials and methods", "in Materials and Methods"),
            ("the results and discussion shows", "the Results and Discussion shows"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_clinical_terms(self):
        """Test clinical and medical terminology rules"""
        test_cases = [
            ("reported adverse event", "reported adverse event (AE)"),
            ("serious adverse event occurred", "serious adverse event (SAE) occurred"),
            ("treatment emergent adverse event", "treatment-emergent adverse event (TEAE)"),
            ("adverse drug reaction", "adverse drug reaction (ADR)"),
            ("investigational product", "investigational product (IP)"),
            ("concomitant medication", "concomitant medication (CM)"),
            ("quality of life assessment", "quality of life (QoL) assessment"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_study_phase_formatting(self):
        """Test study phase formatting rules"""
        test_cases = [
            ("phase 1 study", "Phase 1 study"),
            ("phase i trial", "Phase 1 trial"),
            ("phase two study", "Phase 2 study"),
            ("phase iii trial", "Phase 3 trial"),
            ("phase 4 extension", "Phase 4 extension"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_units_and_numbers(self):
        """Test units and numerical formatting rules"""
        test_cases = [
            ("100mg dose", "100 mg dose"),
            ("50ml volume", "50 mL volume"),
            ("2l fluid", "2 L fluid"),
            ("75kg weight", "75 kg weight"),
            ("approximately 50%", "~50%"),
            ("greater than or equal to 100", "≥100"),
            ("less than or equal to 50", "≤50"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_statistical_terms(self):
        """Test statistical terminology rules"""
        test_cases = [
            ("p-value was 0.05", "P value was 0.05"),
            ("95% ci range", "95% CI range"),
            ("mean (sd)", "mean (SD)"),
            ("standard error (se)", "standard error (SE)"),
            ("itt population", "ITT population"),
            ("pp analysis", "PP analysis"),
            ("odds ratio analysis", "odds ratio (OR) analysis"),
            ("hazard ratio showed", "hazard ratio (HR) showed"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_organizations_and_regulatory(self):
        """Test organization and regulatory body formatting"""
        test_cases = [
            ("submitted to fda", "submitted to FDA"),
            ("ema approval", "EMA approval"),
            ("irb review", "IRB review"),
            ("iec approval", "IEC approval"),
            ("ich guidelines", "ICH guidelines"),
            ("gcp compliance", "GCP compliance"),
            ("daiichi sankyo study", "Daiichi Sankyo study"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_time_points(self):
        """Test time point and study period formatting"""
        test_cases = [
            ("at base-line", "at baseline"),
            ("during follow up", "during follow-up"),
            ("at end of treatment", "at end of treatment (EOT)"),
            ("until end of study", "until end of study (EOS)"),
            ("in screening period", "in Screening Period"),
            ("during treatment period", "during Treatment Period"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_medical_terms(self):
        """Test common medical term formatting"""
        test_cases = [
            ("normal ecg reading", "normal ECG reading"),
            ("scheduled for mri", "scheduled for MRI"),
            ("ct scan results", "CT scan results"),
            ("dna analysis", "DNA analysis"),
            ("rna sequencing", "RNA sequencing"),
            ("pcr test", "PCR test"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_demographics(self):
        """Test demographic term formatting"""
        test_cases = [
            ("bmi calculation", "BMI calculation"),
            ("white subjects", "White subjects"),
            ("black participants", "Black participants"),
            ("asian population", "Asian population"),
            ("other ethnicities", "Other ethnicities"),
            ("male patients", "Male patients"),
            ("female subjects", "Female subjects"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_formatting(self):
        """Test general formatting rules"""
        test_cases = [
            ("i.e.the results", "i.e., the results"),
            ("e.g.the patients", "e.g., the patients"),
            ("treatment vs.control", "treatment vs control"),
            ("etc.and others", "etc. and others"),
        ]
        for input_text, expected in test_cases:
            corrected, _ = self.processor.apply_style_corrections(input_text)
            self.assertEqual(corrected, expected)

    def test_multiple_corrections(self):
        """Test multiple corrections in a single text"""
        input_text = """phase 1 study showed adverse event in white female subjects 
        with bmi >25kg and abnormal ecg. approximately 50% of patients (i.e.100 subjects) 
        were followed during the end of treatment period."""

        expected_text = """Phase 1 study showed adverse event (AE) in White Female subjects 
        with BMI >25 kg and abnormal ECG. ~50% of patients (i.e., 100 subjects) 
        were followed during the end of treatment (EOT) period."""

        corrected, changes = self.processor.apply_style_corrections(input_text)
        self.assertEqual(corrected.strip(), expected_text.strip())
        self.assertGreater(len(changes), 5)  # Should have multiple changes

if __name__ == '__main__':
    unittest.main()
