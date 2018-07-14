self._test_time.start()
        self._block_time.start()
        self._trial_time.start()
        self._block_timeout_timer = QTimer()
        self._trial_timeout_timer = QTimer()

# add a flag to the procedure to say that we resumed the test
        if self.data.test_resumed and not self.data.test_completed:
            self.data.proc.remaining_trials[0].resumed_from_here = True