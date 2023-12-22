import unittest
from unittest.mock import patch, Mock
import numpy as np

import numpy as np
from license_plate_insights.inference import CarLicensePlateDetector, ImageProcessor, ObjectDetector, OCR
from google.cloud import vision
from google.protobuf.json_format import ParseDict
import cv2


class TestCarLicensePlateDetector(unittest.TestCase):

    @patch('license_plate_insights.ocr.OCR')
    @patch('license_plate_insights.object_detection.ObjectDetector')
    @patch('license_plate_insights.image_processing.ImageProcessor')
    def setUp(self, mock_ocr, mock_object_detector, mock_image_processor):
        self.image_processor = mock_image_processor.return_value
        self.object_detector = mock_object_detector.return_value
        self.ocr = mock_ocr.return_value
        self.detector = CarLicensePlateDetector(self.image_processor, self.object_detector, self.ocr)


    @patch('license_plate_insights.inference.CarLicensePlateDetector.annotate_image')
    @patch('license_plate_insights.inference.CarLicensePlateDetector.detect_license_plate')
    def test_recognize_license_plate(self, mock_recognize_license_plate_object, mock_draw_text):
        # Create a mock image
        mock_image = np.zeros((640, 480, 3), dtype=np.uint8)

        # Define test scenarios
        test_scenarios = [
            {
                'recognize_output': ('ABC123', (50, 50, 200, 200)),
                'draw_output': mock_image,
                'expected_result': ('ABC123', mock_image)
            },
            {
                'recognize_output': ('', (50, 50, 200, 200)),
                'draw_output': mock_image,
                'expected_result': ('', mock_image)
            }
        ]

        # Test different scenarios
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario):
                mock_recognize_license_plate_object.return_value = scenario['recognize_output']
                mock_draw_text.return_value = scenario['draw_output']
                result = self.detector.recognize_license_plate('mock_image_path')
                self.assertEqual(result, scenario['expected_result'])

    @patch('license_plate_insights.inference.CarLicensePlateDetector.draw_text')
    def test_draw_text_on_image(self, mock_draw_text):
        mock_draw_text.return_value = 'mock_image_with_text'
        output_image = self.detector.draw_text('mock_image', 'mock_text', (0, 0))
        self.assertEqual(output_image, 'mock_image_with_text')

    # Test case for extract_license_plate_text method
    @patch('google.cloud.vision.ImageAnnotatorClient')
    def test_extract_license_plate_text(self):
        mock_roi = np.random.rand(100, 100, 3) * 255
        mock_roi = mock_roi.astype(np.uint8)
        expected_text = 'TEST1234'
        text_annotation_dict = {'description': expected_text}
        text_annotation = ParseDict(text_annotation_dict, vision.TextAnnotation())
        response_dict = {'text_annotations': [text_annotation], 'error': {'message': ''}}
        response = ParseDict(response_dict, vision.AnnotateImageResponse())

        with patch('cv2.imencode') as mock_imencode, \
            patch('google.cloud.vision.ImageAnnotatorClient') as mock_client:
            mock_imencode.return_value = (None, np.frombuffer(b'mock\x00binary\x00data', dtype=np.uint8))
            mock_client = mock_client.return_value
            mock_client.text_detection.return_value = response
            extracted_text = self.detector.extract_license_plate_text(mock_roi)
            self.assertEqual(extracted_text, expected_text)

    # Test case for load_image method
    @patch('cv2.imdecode')
    @patch('np.fromfile', return_value=np.frombuffer(b'mock binary data', dtype=np.uint8))
    def test_load_image(self, mock_fromfile, mock_imdecode):
        mock_image_path = 'mock_image.jpg'
        mock_returned_image = np.random.rand(100, 100, 3) * 255
        mock_returned_image = mock_returned_image.astype(np.uint8)
        mock_imdecode.return_value = mock_returned_image
        loaded_image = self.detector.load_image(mock_image_path)
        np.testing.assert_array_equal(loaded_image, mock_returned_image[:, :, ::-1])

    # Test case for process_video method
    @patch('cv2.VideoCapture')
    @patch('cv2.VideoWriter')
    @patch('license_plate_insights.inference.CarLicensePlateDetector.process_video')
    def test_process_video(self, mock_process_video, mock_video_writer, mock_video_capture):
        mock_process_video.return_value = None
        mock_video_path = 'mock_video_path.mp4'
        mock_output_path = 'mock_output_path.mp4'
        self.detector.process_video(mock_video_path, mock_output_path)
        mock_process_video.assert_called_once_with(mock_video_path, mock_output_path)

    def test_detect_license_plate(self):
        with patch('license_plate_insights.object_detection.ObjectDetector.recognize_license_plate') as mock_recognize_license_plate:
            # Setup mocks
            mock_image = np.zeros((640, 480, 3), dtype=np.uint8)
            expected_output = ('ABC123', np.array([50, 50, 200, 200]))
            mock_recognize_license_plate.return_value = expected_output

            # Call the function
            recognized_text, roi = self.detector.detect_license_plate(mock_image)

            # Assertions
            mock_recognize_license_plate.assert_called_once_with(mock_image)
            self.assertEqual(recognized_text, expected_output[0])
            np.testing.assert_array_equal(roi, expected_output[1])

    def test_annotate_image(self):
        with patch('license_plate_insights.inference.ImageProcessor.draw_text') as mock_draw_text, \
             patch('license_plate_insights.inference.CarLicensePlateDetector.load_image', return_value='mock_image'):
            # Setup mocks
            recognized_text = 'test_plate'
            roi = (50, 50, 200, 200)
            mock_draw_text.return_value = 'mock_annotated_image'

            # Call the function
            annotated_image = self.detector.annotate_image(recognized_text, roi, 'mock_image')

            # Assertions
            mock_draw_text.assert_called_once_with('mock_image', recognized_text, (roi[0], roi[1] - 20))
            self.assertEqual(annotated_image, 'mock_annotated_image')

if __name__ == '__main__':
    unittest.main()
