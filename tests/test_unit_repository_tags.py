import pytest

from src.database.models import Tag
from src.repository.tags import get_or_create_tag


# Mock database session
class MockSession:
    """
    Mock session object simulating the behavior of a database session.

    This class is used to create a mock session object that mimics the behavior
    of a real database session for testing purposes.

    """

    def query(self, *args, **kwargs):
        """
        Simulate the query method of a database session.

        This method returns the current instance of the MockSession object
        to simulate the behavior of the query method in a real database session.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            MockSession: The current instance of the MockSession object.

        """
        return self

    def filter(self, *args, **kwargs):
        """
        Simulate the filter method of a database session.

        This method returns the current instance of the MockSession object
        to simulate the behavior of the filter method in a real database session.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            MockSession: The current instance of the MockSession object.

        """
        return self

    def first(self):
        """
        Simulate the first method of a database session.

        This method returns None to simulate the behavior of the first method
        in a real database session, indicating that the requested object does not exist.

        Returns:
            None: None object indicating that the requested object does not exist.

        """
        return None

    def add(self, obj):
        """
        Simulate the add method of a database session.

        This method does nothing as it is used only for simulating the behavior
        of the add method in a real database session.

        Args:
            obj: Object to be added to the session.

        """
        pass

    def commit(self):
        """
        Simulate the commit method of a database session.

        This method does nothing as it is used only for simulating the behavior
        of the commit method in a real database session.

        """
        pass

    def refresh(self, obj):
        """
        Simulate the refresh method of a database session.

        This method does nothing as it is used only for simulating the behavior
        of the refresh method in a real database session.

        Args:
            obj: Object to be refreshed in the session.

        """
        pass


def test_get_or_create_tag():
    """
    Test the get_or_create_tag function.

    This test function verifies the behavior of the get_or_create_tag function
    by mocking a database session and testing whether the function correctly
    creates a new tag with the specified tag name.

    """
    mock_db_session = MockSession()
    tag_name = "test_tag"

    created_tag = get_or_create_tag(mock_db_session, tag_name)

    assert isinstance(created_tag, Tag)
    assert created_tag.tag_name == tag_name


def test_get_existing_tag(mocker):
    """
    Test if an existing tag is retrieved when it already exists.

    This test function mocks a database session and verifies that the
    get_or_create_tag function retrieves an existing tag when it already exists
    in the database.
    """
    mock_session = mocker.MagicMock()
    existing_tag_name = "existing_tag"
    existing_tag = Tag(tag_name=existing_tag_name)
    mock_session.query().filter().first.return_value = existing_tag
    retrieved_tag = get_or_create_tag(mock_session, existing_tag_name)
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    assert retrieved_tag == existing_tag


def test_multiple_calls_same_tag_name(mocker):
    """
    Test if multiple calls with the same tag name return the same tag instance.

    This test function mocks a database session and verifies that multiple calls
    to the get_or_create_tag function with the same tag name return the same
    tag instance.
    """
    mock_session = mocker.MagicMock()
    tag_name = "test_tag"
    first_call_tag = get_or_create_tag(mock_session, tag_name)
    second_call_tag = get_or_create_tag(mock_session, tag_name)
    assert first_call_tag is second_call_tag


def test_case_insensitive_tag_names(mocker):
    """
    Test if tag names are case-insensitive.

    This test function mocks a database session and verifies that tag names are
    case-insensitive when checking for existing tags in the database.
    """
    mock_session = mocker.MagicMock()
    tag_name = "Test_Tag"
    lowercase_tag_name = "test_tag"
    existing_tag = Tag(tag_name=tag_name)
    mock_session.query().filter().first.return_value = existing_tag
    retrieved_tag = get_or_create_tag(mock_session, lowercase_tag_name)
    assert retrieved_tag is existing_tag


def test_empty_or_whitespace_tag_name(mocker):
    """
    Test if ValueError is raised for empty or whitespace tag names.

    This test function mocks a database session and verifies that ValueError
    is raised when the tag name provided to the get_or_create_tag function is
    empty or consists only of whitespace.
    """
    mock_session = mocker.MagicMock()
    empty_tag_name = ""
    whitespace_tag_name = "   "
    with pytest.raises(ValueError):
        get_or_create_tag(mock_session, empty_tag_name)
    with pytest.raises(ValueError):
        get_or_create_tag(mock_session, whitespace_tag_name)
