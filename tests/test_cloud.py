import unittest
from unittest.mock import patch
from figranium_client import FigraniumClient, FigraniumError

class CloudTests(unittest.TestCase):
    def test_cloud_routes_and_variable_guard(self):
        client = FigraniumClient("https://cloud.figranium.dev", "key", 5)
        with patch.object(FigraniumClient, "_request", side_effect=[[{"id": "t1"}], {"id": "e1", "status": "queued"}]) as request:
            self.assertEqual(client.list_tasks(), {"tasks": [{"id": "t1"}]})
            self.assertEqual(client.execute_task("t1", {})["status"], "queued")
            self.assertEqual(request.call_args_list[0].args, ("GET", "/api/v1/tasks"))
            self.assertEqual(request.call_args_list[1].args, ("POST", "/api/v1/executions", {"taskId": "t1"}))
            with self.assertRaisesRegex(FigraniumError, "no execution was started"):
                client.execute_task("t1", {"x": "y"})
            self.assertEqual(request.call_count, 2)

    def test_self_hosted_stays_on_existing_routes(self):
        client = FigraniumClient("https://example.com", "key", 5)
        with patch.object(FigraniumClient, "_request", return_value={"tasks": []}) as request:
            client.list_tasks()
            request.assert_called_once_with("GET", "/api/tasks/list")
