from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .core import NewMessage, PythonTaReporter

if TYPE_CHECKING:
    from pylint.lint import PyLinter
    from pylint.reporters.ureports.nodes import BaseLayout


class JSONReporter(PythonTaReporter):
    """Reporter that outputs JSON.

    Based on Pylint's JSONReporter.
    """

    name = "pyta-json"

    OUTPUT_FILENAME = "pyta_report.json"

    messages: dict[str, list[NewMessage]]

    def display_messages(self, layout: BaseLayout) -> None:
        """Hook for displaying the messages of the reporter

        This will be called whenever the underlying messages
        needs to be displayed. For some reporters, it probably
        doesn't make sense to display messages as soon as they
        are available, so some mechanism of storing them could be used.
        This method can be implemented to display them after they've
        been aggregated.
        """
        output = []
        for k, msgs in self.messages.items():
            output.append(
                {
                    "filename": k,
                    "msgs": self._output_messages(msgs),
                }
            )

        self.writeln(json.dumps(output, indent=4))
        self.out.flush()

    def _output_messages(self, msgs: list[NewMessage]) -> list[dict]:
        """Returns a list of dictionaries containing formatted error messages."""
        max_messages = self.linter.config.pyta_number_of_messages
        num_occurrences = {msg.message.msg_id: 0 for msg in msgs}
        output_lst = []

        for msg in msgs:
            if max_messages == 0 or num_occurrences[msg.message.msg_id] < max_messages:
                output_lst.append(msg.to_dict())
            num_occurrences[msg.message.msg_id] += 1

        for msg_dict in output_lst:
            msg_dict["number_of_occurrences"] = num_occurrences[msg_dict["msg_id"]]

        return output_lst


def register(linter: PyLinter):
    linter.register_reporter(JSONReporter)
