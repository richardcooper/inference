class NoProofFoundError(Exception):
    """Raised by `Rules.prove(goal)` if `goal` cannot be proved."""

class MultipleProofsError(Exception):
    """Raised by `Rules.prove(goal, unambiguously=True)` if `goal` has multiple proofs."""
