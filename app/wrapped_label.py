from kivy.uix.label import Label


class WrappedLabel(Label):
    """
    A subclass of Label which supports wrapping text automatically.
    """

    # Courtesy of https://stackoverflow.com/questions/43666381/wrapping-the-text-of-a-kivy-label
    def __init__(self, **kwargs):
        """
        Creates a WrappedLabel object
        :param kwargs: Arguments for Label
        """
        super().__init__(**kwargs)
        self.bind(
            width=lambda *x: self.setter("text_size")(self, (self.width, None)),
            texture_size=lambda *x: self.setter("height")(self, self.texture_size[1]),
        )
