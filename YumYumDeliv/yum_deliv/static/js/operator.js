document.addEventListener('DOMContentLoaded', function () {
    var feedbackListItems = document.querySelectorAll('.feedback-list');

    feedbackListItems.forEach(function (item) {
        item.addEventListener('click', function () {
            var feedbackId = item.getAttribute('data-feedback-id');

            var feedbackDetailBlocks = document.querySelectorAll('[id^="od-"]');
            feedbackDetailBlocks.forEach(function (block) {
                block.hidden = true;
            });

            var selectedFeedbackDetailBlock = document.getElementById('od-' + feedbackId);
            if (selectedFeedbackDetailBlock) {
                selectedFeedbackDetailBlock.hidden = false;
            }
        });
    });
});
