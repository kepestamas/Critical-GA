import os
import tempfile
import unittest

from graph_io import read_graph


class ReadGraphTest(unittest.TestCase):
    def test_reads_colon_adjacency_lists_without_trailing_colons(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as tmp:
            tmp.write("3\n0: 1 2\n1: 0\n2: 0\n")
            path = tmp.name

        try:
            graph, weights = read_graph(path, detect_weights=True)

            self.assertEqual(set(graph.nodes()), {"0", "1", "2"})
            self.assertTrue(graph.has_edge("0", "1"))
            self.assertTrue(graph.has_edge("0", "2"))
            self.assertEqual(weights["0"], 1)
            self.assertEqual(weights["1"], 1)
            self.assertEqual(weights["2"], 1)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
