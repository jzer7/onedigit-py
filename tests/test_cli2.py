import unittest
import tempfile
import os
import json
import sys
from unittest.mock import patch
from io import StringIO

from onedigit.cli2 import main_cli2, main, create_parser


class TestCli2(unittest.TestCase):
    """Test cases for the new argparse-based CLI."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: self._cleanup_temp_dir())

    def _cleanup_temp_dir(self):
        """Clean up temporary directory."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_parser_creation(self):
        """Test that the argument parser is created correctly."""
        parser = create_parser()
        self.assertIsNotNone(parser)
        self.assertEqual(parser.prog, 'onedigit')

    def test_main_basic_functionality(self):
        """Test basic functionality with valid inputs."""
        result = main(digit=3, max_value=10, max_cost=2, max_steps=2)
        self.assertTrue(result)

    def test_main_with_invalid_digit_range(self):
        """Test error handling for digit out of range."""
        # Test digit too low
        result = main(digit=0, max_value=10)
        self.assertFalse(result)
        
        # Test digit too high
        result = main(digit=10, max_value=10)
        self.assertFalse(result)

    def test_main_with_invalid_digit_type(self):
        """Test error handling for non-integer digit."""
        result = main(digit="not_a_number", max_value=10)
        self.assertFalse(result)

    def test_main_with_invalid_parameters(self):
        """Test error handling for invalid parameter types."""
        result = main(digit=3, max_value="invalid", max_cost=2)
        self.assertFalse(result)

    def test_main_with_nonexistent_input_file(self):
        """Test error handling for non-existent input file."""
        result = main(digit=3, input_filename="nonexistent_file.json")
        self.assertFalse(result)

    def test_main_with_invalid_input_filename_type(self):
        """Test error handling for invalid input filename type."""
        result = main(digit=3, input_filename=123)
        self.assertFalse(result)

    def test_main_with_invalid_output_filename_type(self):
        """Test error handling for invalid output filename type."""
        result = main(digit=3, output_filename=123)
        self.assertFalse(result)

    def test_main_with_valid_json_input(self):
        """Test loading a valid JSON input file."""
        # Create a test JSON file with proper structure
        test_data = {
            "digit": 3,
            "max_value": 100,
            "max_cost": 3,
            "combinations": []  # This should be a list, not a dict
        }
        
        json_file = os.path.join(self.temp_dir, "test_input.json")
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        result = main(digit=3, input_filename=json_file, max_value=10)
        self.assertTrue(result)

    def test_main_with_output_file(self):
        """Test creating an output file."""
        output_file = os.path.join(self.temp_dir, "test_output.json")
        
        result = main(digit=3, max_value=10, output_filename=output_file)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify the output file contains valid JSON
        with open(output_file, 'r') as f:
            data = json.load(f)
            self.assertIsInstance(data, dict)

    def test_main_with_permission_error_input(self):
        """Test error handling for permission error on input file."""
        # Create a file and remove read permissions
        test_file = os.path.join(self.temp_dir, "no_read.json")
        with open(test_file, 'w') as f:
            f.write('{"digit": 3}')
        
        os.chmod(test_file, 0o000)  # Remove all permissions
        
        result = main(digit=3, input_filename=test_file)
        self.assertFalse(result)
        
        # Restore permissions for cleanup
        os.chmod(test_file, 0o644)

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_output_format_simple(self, mock_stdout):
        """Test output format with simple expressions."""
        result = main(digit=3, max_value=10, full=False)
        self.assertTrue(result)
        
        output = mock_stdout.getvalue()
        self.assertIn("=", output)
        self.assertIn("[", output)  # Cost indicator

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_output_format_full(self, mock_stdout):
        """Test output format with full expressions."""
        result = main(digit=3, max_value=10, full=True)
        self.assertTrue(result)
        
        output = mock_stdout.getvalue()
        self.assertIn("=", output)
        self.assertIn("[", output)  # Cost indicator

    def test_cli2_with_valid_args(self):
        """Test main_cli2 with valid command line arguments."""
        args = ['3', '--max-value', '10', '--max-cost', '2']
        result = main_cli2(args)
        self.assertTrue(result)

    def test_cli2_with_help(self):
        """Test main_cli2 with help argument."""
        args = ['--help']
        result = main_cli2(args)
        # Help should return True (exit code 0)
        self.assertTrue(result)

    def test_cli2_with_invalid_args(self):
        """Test main_cli2 with invalid arguments."""
        args = ['invalid_digit']
        result = main_cli2(args)
        self.assertFalse(result)

    def test_cli2_missing_required_args(self):
        """Test main_cli2 with missing required arguments."""
        args = []
        result = main_cli2(args)
        self.assertFalse(result)

    def test_cli2_with_full_flag(self):
        """Test main_cli2 with full flag."""
        args = ['3', '--full', '--max-value', '10']
        result = main_cli2(args)
        self.assertTrue(result)

    def test_cli2_with_input_file(self):
        """Test main_cli2 with input file."""
        # Create a test JSON file with proper structure
        test_data = {"digit": 3, "max_value": 100, "max_cost": 3, "combinations": []}
        json_file = os.path.join(self.temp_dir, "test_input.json")
        with open(json_file, 'w') as f:
            json.dump(test_data, f)
        
        args = ['3', '--input-filename', json_file, '--max-value', '10']
        result = main_cli2(args)
        self.assertTrue(result)

    def test_cli2_with_output_file(self):
        """Test main_cli2 with output file."""
        output_file = os.path.join(self.temp_dir, "test_output.json")
        
        args = ['3', '--output-filename', output_file, '--max-value', '10']
        result = main_cli2(args)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_file))

    def test_cli2_argument_parsing_edge_cases(self):
        """Test edge cases in argument parsing."""
        # Test with all arguments
        output_file = os.path.join(self.temp_dir, "test_output.json")
        args = [
            '5',
            '--max-value', '100',
            '--max-cost', '3',
            '--max-steps', '10',
            '--full',
            '--output-filename', output_file
        ]
        result = main_cli2(args)
        self.assertTrue(result)

    def test_main_zero_max_value(self):
        """Test behavior with zero max_value."""
        # Zero max_value should fail as the model requires max_value >= 1
        result = main(digit=3, max_value=0, max_cost=2)
        self.assertFalse(result)

    def test_main_large_parameters(self):
        """Test with large parameter values."""
        result = main(digit=3, max_value=100000, max_cost=10, max_steps=1)
        self.assertTrue(result)

    def test_main_automatic_output_filename(self):
        """Test that automatic output filename generation works."""
        # When output_filename is empty, it should generate a filename
        result = main(digit=3, max_value=10, output_filename="")
        self.assertTrue(result)

    def test_compatibility_with_original_cli(self):
        """Test that new CLI produces same results as original CLI core logic."""
        # Import the original main function
        from onedigit.cli import main as original_main
        
        # Test with same parameters
        digit = 3
        max_value = 10
        max_cost = 2
        max_steps = 2
        
        # Both should return True for valid inputs
        original_result = original_main(
            digit=digit, 
            max_value=max_value, 
            max_cost=max_cost, 
            max_steps=max_steps,
            output_filename="/tmp/test_original.json"
        )
        
        new_result = main(
            digit=digit, 
            max_value=max_value, 
            max_cost=max_cost, 
            max_steps=max_steps,
            output_filename="/tmp/test_new.json"
        )
        
        self.assertEqual(original_result, new_result)


if __name__ == '__main__':
    unittest.main()