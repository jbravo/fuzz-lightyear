from fuzz_lightyear import main
from testing.mock_server import PORT
from testing.mock_server import URL


class TestMain:
    def test_returns_one_if_failure(self):
        assert main.main([URL])

    def test_success(self, mock_client):
        # TODO: This is more of a smoke test right now. It flags,
        #       because it identifies IDOR, but this also masks other errors.
        #       We should address this again, when we implement whitelist
        #       functionality.
        assert main.main([
            '{}/schema'.format(URL),
            '-f', 'test_data/nested',
        ])

    def test_ignore_exceptions_hides_exceptions(self, mock_client):
        assert not main.main([
            '{}/schema'.format(URL),
            '-t', 'constant.get_will_throw_error',
            '--ignore-exceptions',
        ])

    def test_ignore_exceptions_still_shows_vulnerabilities(self, mock_client):
        assert main.main([
            '{}/schema'.format(URL),
            '-t', 'constant.get_will_throw_error',
            '-t', 'basic.get_private_listing',
            '--ignore-exceptions',
            '-f', 'test_data/nested',
        ])


class TestSetupClient:
    def test_unable_to_connect_to_url(self, mock_server):
        url = 'http://localhost:{}'.format(PORT + 1)
        assert main.setup_client(url) == 'Unable to connect to server.'

    def test_invalid_schema_at_url(self, mock_server):
        assert 'Invalid swagger file.' in main.setup_client(URL)

    def test_success_with_url_only(self, mock_server):
        assert not main.setup_client('{}/schema'.format(URL))

    def test_provided_schema_not_swagger_file(self, mock_server):
        assert main.setup_client(
            URL,
            {
                'hello': 'world',
            },
        ) == 'Invalid swagger format.'

    def test_success_with_provided_schema(self, mock_server, mock_schema):
        assert not main.setup_client(URL, mock_schema)
