from skbio._base import SkbioObject
from skbio.util._decorator import experimental





class Feature(SkbioObject):
    """
    Stores genbank sequence feature records
    """

    @experimental(as_of="0.4.2")
    def __init__(self, type, location, qualifiers = None):
        self.type_ = type

        # original location string is kept as well as parsed into
        # attributes describing location
        self.location = location
        self.rc_ = False
        self.left_partial_ = False
        self.right_partial_ = False
        self.begin = 0
        self.end = 0
        self.qualifiers = qualifiers


    @experimental(as_of="0.4.2")
    def __str__(self):
        # TODO: string output for debugging/stdout display
        pass

    @experimental(as_of="0.4.2")
    def __repr__(self):
        # TODO: string output that meet genbank file specification
        pass




