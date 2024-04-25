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
