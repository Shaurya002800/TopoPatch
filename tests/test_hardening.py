import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from topopatch.demo import fixture
from topopatch.engine import Engine, MigrationError

class HardeningTests(unittest.TestCase):
    def test_strict_preview_reports_policy_refusal(self):
        e=Engine(require_bounded_evidence=True); self.addCleanup(e.db.close); e.initialize(fixture())
        p=e.preview(['password-policy'])
        self.assertTrue(p['barrier']['pass']); self.assertFalse(p['admission']['allowed'])
        with self.assertRaisesRegex(MigrationError,'unbounded'): e.commit(p['id'])

    def test_exhaustive_admission_requires_current_coverage(self):
        e=Engine(require_bounded_evidence=True,exhaustive_evidence=True); self.addCleanup(e.db.close); e.initialize(fixture())
        self.assertFalse(e.preview(['password-policy'])['admission']['allowed'])
        e.envelope(); self.assertTrue(e.preview(['password-policy'])['admission']['allowed'])
        e.update_source('car-guide','modified source')
        self.assertFalse(e.preview(['password-policy'])['admission']['allowed'])

    def test_rollback_excludes_external_writer_during_check(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'state.sqlite'
            e=Engine(path); self.addCleanup(e.db.close); e.initialize(fixture())
            e.commit(e.propose()['recommended']['preview_id'])
            other=sqlite3.connect(path,timeout=0); self.addCleanup(other.close)
            attempts=[]
            def attempt_write(sql):
                if sql.startswith('SELECT payload FROM events'):
                    try:
                        other.execute("UPDATE docs SET version=version+1 WHERE id='car-guide'")
                        other.commit(); attempts.append('write succeeded')
                    except sqlite3.OperationalError as exc:
                        attempts.append(str(exc)); other.rollback()
            e.db.set_trace_callback(attempt_write)
            e.rollback(); e.db.set_trace_callback(None)
            self.assertEqual(attempts,['database is locked'])
            self.assertEqual(e.status()['active_b'],0)

    def test_rollback_write_failure_is_atomic(self):
        e=Engine(); self.addCleanup(e.db.close); e.initialize(fixture())
        e.commit(e.propose()['recommended']['preview_id']); before=e.export(); snapshot=e.snapshot()
        e.db.execute("CREATE TRIGGER fail_rollback BEFORE UPDATE OF active ON docs BEGIN SELECT RAISE(ABORT,'rollback fault'); END")
        with self.assertRaisesRegex(sqlite3.IntegrityError,'rollback fault'): e.rollback()
        self.assertEqual(e.snapshot(),snapshot); self.assertEqual(e.export(),before)

    def test_rollback_after_source_update_refused(self):
        e=Engine(); self.addCleanup(e.db.close); e.initialize(fixture())
        e.commit(e.propose()['recommended']['preview_id']); e.update_source('car-guide','changed')
        before=e.snapshot()
        with self.assertRaisesRegex(MigrationError,'unchanged'): e.rollback()
        self.assertEqual(e.snapshot(),before)
