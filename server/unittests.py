import unittest


class TestLanguageServer(unittest.TestCase):
    def test_code_completion_provider(self):
        ''' Test code completion provider '''
        pass
    def test_definition_provider(self):
        ''' Test defintion provider '''
        pass
    def test_diagnostic_provider(self):
        ''' Test diganostic provider '''
        pass
    def test_highlight_provider(self):
        ''' Test highlight provider '''
        pass
    def test_reference_provider(self):
        ''' Test reference provider '''
        pass
    def test_rename_provider(self):
        ''' Test rename provider '''
        pass
    def transport_kind_opened(self):
        ''' Ensure the transport mechanism is properly opened '''
        pass
    def transport_kind_closed(self):
        ''' Ensure the transport mechanism is properly closed '''
        pass

if __name__ == "__main__":
    unittest.main()
