

def invert_spans(spans, span_min_max=None, in_place=False):
    """Inverts the list of provided spans and clamps the inversion between the specified minimum and maximum.

    Return a list of spans that are the result of the inversion of the provide spans clamped by the provided range.

    :param spans: List of span tuples [(min, max), ..., ] to invert, where each span is [min, max)
    :param span_min_max: Span tuple to clamp the inversion against, where the span is [min, max]
    :return: List of span tuples [(min, max), ..., ] generated by inverting the provided spans, where each span is [min, max)
    """
    if spans is None:
        raise ValueError('spans cannot be None')
    if span_min_max and span_min_max[1] < span_min_max[0]:
        raise ValueError('span max must be greater than span min')

    # Empty list is just the span minimum and span maximum provided.
    if span_min_max and len(spans) == 0:
        if in_place:
            spans[:] = [(span_min_max[0], span_min_max[1])]
            return
        else:
            return [(span_min_max[0], span_min_max[1])]

    # Sort and merge the spans.
    if in_place:
        merge_spans(spans, in_place=True)
    else:
        spans = merge_spans(spans)

    # Check that the span minimum and maximum range fits the span list.
    if span_min_max and spans[0][0] < span_min_max[0]:
        raise ValueError('span min must be less than or equal to the smallest span start')
    if span_min_max and spans[-1][1] > span_min_max[1]:
        raise ValueError('span max must be greater than or equal to the largest span end')

    # Store the minimum and maximum value before modifying the list.
    span_min = spans[0][0]
    span_max = spans[-1][1]

    # Invert all spans in the span list.
    i = len(spans) - 1
    while i > 0:
        s = spans[i]
        t = spans[i - 1]
        del spans[i]
        spans.insert(i, (t[1], s[0]))
        i -= 1

    # The first span should always be removed after inversion because it cannot be inverted.
    del spans[0]

    # Add the minimum inverted span if necessary.
    if span_min_max:
        # Could be an empty list.
        if len(spans) == 0:
            if span_min_max[0] != span_min:
                spans.append((span_min_max[0], span_min))
        else:
            if span_min_max[0] != span_min:
                spans.insert(0, (span_min_max[0], span_min))

    # Add the maximum inverted span if necessary.
    if span_min_max:
        if span_min_max[1] != span_max:
            spans.append((span_max, span_min_max[1]))

    if not in_place:
        return spans


def merge_spans(spans, in_place=False):
    """Sorts and merges a list of spans.

    Return a list of spans that are the result of sorting and merging the provided spans.

    :param spans: List of span tuples [(min, max), ..., ] to sort and merge, where each span is [min, max)
    :return: List of spans [(min, max), ..., ] generated by sorting and merging the provided spans, where each span is [min, max)
    """
    if spans is None:
        raise ValueError('spans cannot be None')

    # Pre-sort the span list.
    if in_place:
        spans.sort()
    else:
        spans = sorted(spans)


    # Loop through all spans, attempting to merge them.
    i = len(spans) - 1
    while i >= 0:
        # Pick a span to attempt to merge others into.
        current_span = spans[i]
        current_min = current_span[0]
        current_max = current_span[1]
        # Skip empty spans.
        if current_min == current_max:
            # Delete the empty span.
            del spans[i]
            i -= 1
            continue
        elif current_max < current_min:
            raise ValueError('max must be greater than min')
        # Loop through all other remaining spans.
        j = i - 1
        while j >= 0:
            # Pick a candidate span to attempt to merge into current span.
            candidate_span = spans[j]
            candidate_min = candidate_span[0]
            candidate_max = candidate_span[1]
            # Skip empty spans.
            if candidate_min == candidate_max:
                # Delete the empty span.
                del spans[j]
                i -= 1
                j = i - 1
                continue
            elif candidate_max < candidate_min:
                raise ValueError('max must be greater than min')
            # If the candidate span overlaps or is adjacent, merge it.
            if current_min <= candidate_max and candidate_min <= current_max:
                # Select the smallest minimum and largest maximum of the two spans.
                # The merge result becomes the current span.
                current_span = (current_min if current_min <= candidate_min else candidate_min, current_max if current_max >= candidate_max else candidate_max)
                current_min = current_span[0]
                current_max = current_span[1]
                j -= 1
            # Could not merge candidate span.
            else:
                break

        # Check if any merges occurred.
        # Does not check in_place because spans list would have already been copied.
        if j != (i - 1):
            del spans[j + 1 : i + 1]
            spans.insert(j + 1, current_span)

        i = j

    if not in_place:
        return spans


class SpanSet:
    def __init__(self, spans=[]):
        """Create a new SpanSet instance.

        :param spans: List of span tuples [(min, max), ..., ] to initialize the set with, where each span is [min, max)
        :return: SpanSet
        """
        self.spans = merge_spans(spans)


    def add(self, span):
        """Add a single span to the span set.

        Triggers a sort and merge of the span set.

        :param span: Span tuple (min, max) to add to the span set, where the span is [min, max)
        :return: None
        """
        self.spans.append(span)
        merge_spans(self.spans, in_place=True)


    def extend(self, spans):
        """Add a list of spans to the span set.

        Triggers a sort and merge of the span set.

        :param spans: List of span tuples [(min, max), ..., ] to initialize the set with, where each span is [min, max)
        :return: None
        """
        self.spans.extend(spans)
        merge_spans(self.spans, in_place=True)


    def minimum(self):
        """Find and return the minimum value in the span set.

        :return: The minimum value in the span set, inclusive
        """
        return self.spans[0][0]


    def maximum(self):
        """Find and return the maximum value in the span set.

        :return: The maximum value in the span set, exclusive
        """
        return self.spans[-1][1]


    def inside(self, value):
        """Check if a value intersects the span set.

        :param value: Value to check for intersection with the set
        :return: True if the value intersects the set; otherwise, False
        """
        for s in self.spans:
            if s[0] <= value < s[1]:
                return True
        return False


    def invert(self, span_min_max=None):
        """Invert the span set and returns a new span set.

        :param span_min: Minimum value to clamp the inversion against
        :param span_max: Maximum value to clamp the inversion against
        :return: SpanSet that is the result of the inversion of this SpanSet
        """
        s = SpanSet()
        s.spans = invert_spans(self.spans, span_min_max=span_min_max)
        return s
