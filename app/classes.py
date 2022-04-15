
class DataMatrix:
    def __init__(self):
        image = None
        bbox = None
        parent_image_shape = None
        decoded_successful: bool = None
        decoded_info: str = None

class TargetImage:
    def __init__(self, path_to_original):
        self.path_to_original = path_to_original
        self.data_matrices = None

    
