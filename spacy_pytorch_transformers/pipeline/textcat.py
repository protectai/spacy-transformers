import spacy.pipeline
from ..model_registry import get_model_function

DEBUG_LOSS = False


class PyTT_TextCategorizer(spacy.pipeline.TextCategorizer):
    """Subclass of spaCy's built-in TextCategorizer component that supports
    using the features assigned by the PyTorch-Transformers models via the token
    vector encoder. It requires the PyTT_TokenVectorEncoder to run before it in
    the pipeline.
    """

    name = "pytt_textcat"

    @classmethod
    def from_nlp(cls, nlp, **cfg):
        """Factory to add to Language.factories via entry point."""
        return cls(nlp.vocab, **cfg)

    @classmethod
    def Model(cls, nr_class=1, exclusive_classes=False, **cfg):
        """Create a text classification model using a PyTorch-Transformers model
        for token vector encoding.

        nr_class (int): Number of classes.
        width (int): The width of the tensors being assigned.
        exclusive_classes (bool): Make categories mutually exclusive.
        **cfg: Optional config parameters.
        RETURNS (thinc.neural.Model): The model.
        """
        make_model = get_model_function(cfg.get("architecture", "softmax_class_vector"))
        return make_model(nr_class, exclusive_classes=exclusive_classes, **cfg)

    def get_loss(self, docs, golds, scores):
        # This is a useful diagnostic while figuring out whether your model is
        # learning anything. We print the loss each batch, and also the
        # mean and variance for the score of the first class.
        # If the model is learning things, we want to see the mean score stay
        # close the the class distribution (e.g. 0.5 for balanced classes),
        # while the variance in scores should increase (i.e. different examples
        # should get different scores).
        loss, d_scores = super().get_loss(docs, golds, scores)
        mean_score = scores.mean(axis=0)[0]
        var_score = scores.var(axis=0)[0]
        if DEBUG_LOSS:
            print("L", "%.4f" % loss, "m", "%.3f" % mean_score, "v", "%.6f" % var_score)
        return loss, d_scores
