class Resource:
    """TODO: summary.

    TODO: description.
    """

    name: str
    resource_type: str

    def __init__(self, name: str):
        """Create a resource.

        Args:
            name (str): Descriptive name of the resource.
        """
        self.name = name
