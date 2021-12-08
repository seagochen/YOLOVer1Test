from CvTools.NetworkDetectedResult import NetworkDetectedResult


class YoloGrids(object):

    def __init__(self, grids_cols, grids_rows, confidences, bounding_boxes, object_categories):
        # create the grids for yolo detection model
        self.grids = NetworkDetectedResult(
            grids_cols=grids_cols,
            grids_rows=grids_rows,
            confidences=confidences,
            bounding_boxes=bounding_boxes,
            object_categories=object_categories)

    def use_yolo_style_mark(self, target, left_x, top_y, right_x, bottom_y):

        return target
