import json

import pandas as pd
import pytest

from seabornmasterpro import benchmark, datasets, repro


class TestRepro:
    def test_set_seed_reproducible(self):
        a = repro.set_seed(3).normal(size=3)
        b = repro.set_seed(3).normal(size=3)
        assert (a == b).all()

    def test_capture_environment_fields(self):
        env = repro.capture_environment({"experiment": "x"})
        assert env["experiment"] == "x"
        assert {"python", "platform", "packages", "timestamp_utc", "seabornmasterpro"} <= set(env)
        assert "seaborn" in env["packages"]
        json.dumps(env)  # serialisable

    def test_git_revision_outside_repo(self, tmp_path):
        assert repro.git_revision(tmp_path) is None

    def test_manifest_roundtrip(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text("hello")
        man = repro.write_manifest([f], tmp_path / "MANIFEST.json", relative_to=tmp_path, extra={"seed": 1})
        assert man["files"]["a.txt"]["bytes"] == 5
        assert man["seed"] == 1
        assert repro.verify_manifest(tmp_path / "MANIFEST.json") == {"a.txt": True}
        f.write_text("tampered")
        assert repro.verify_manifest(tmp_path / "MANIFEST.json") == {"a.txt": False}

    def test_sha256_known(self, tmp_path):
        f = tmp_path / "e"
        f.write_bytes(b"")
        assert repro.file_sha256(f) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


class TestDatasets:
    def test_generate_all_and_manifest(self, tmp_path):
        paths = datasets.generate_all(tmp_path, verbose=False)
        assert set(paths) == set(datasets.REGISTRY)
        assert (tmp_path / "MANIFEST.json").exists()
        assert all(repro.verify_manifest(tmp_path / "MANIFEST.json").values())

    def test_deterministic(self, tmp_path):
        p1 = datasets.generate_all(tmp_path / "a", manifest=False, verbose=False)
        p2 = datasets.generate_all(tmp_path / "b", manifest=False, verbose=False)
        for name in p1:
            assert p1[name].read_bytes() == p2[name].read_bytes()

    def test_row_counts_match_cards(self, tmp_path):
        datasets.generate_all(tmp_path, manifest=False, verbose=False)
        for name, card in datasets.REGISTRY.items():
            assert len(pd.read_csv(tmp_path / card.filename)) == card.n_rows

    def test_load_parses_dates(self, tmp_path):
        datasets.generate_all(tmp_path, manifest=False, verbose=False)
        df = datasets.load("sensor_readings", tmp_path)
        assert pd.api.types.is_datetime64_any_dtype(df["Timestamp"])
        with pytest.raises(KeyError):
            datasets.load("missing", tmp_path)

    def test_clinical_trial_planted_effect(self, tmp_path):
        from seabornmasterpro.stats import cohens_d

        datasets.generate_all(tmp_path, manifest=False, verbose=False)
        df = datasets.load("clinical_trial", tmp_path)
        d = cohens_d(df.loc[df.Arm == "High Dose", "Outcome"], df.loc[df.Arm == "Placebo", "Outcome"])
        assert 0.4 < d < 1.2

    def test_repo_csvs_match_manifest(self):
        manifest = datasets.default_dir() / "MANIFEST.json"
        if not manifest.exists():
            pytest.skip("manifest not generated")
        assert all(repro.verify_manifest(manifest).values())

    def test_cli_list(self, capsys):
        assert datasets.main(["--list"]) == 0
        assert "clinical_trial" in capsys.readouterr().out


class TestBenchmark:
    def test_make_data(self):
        df = benchmark.make_data(50)
        assert len(df) == 50 and set(df.columns) == {"x", "y", "t", "g"}

    def test_time_call(self):
        t = benchmark.time_call(lambda: None, repeats=3, warmup=1)
        assert len(t) == 3 and all(x >= 0 for x in t)

    @pytest.mark.slow
    def test_run_and_plot(self, tmp_path):
        cases = {k: benchmark.DEFAULT_CASES[k] for k in ("scatterplot", "boxplot")}
        res = benchmark.run_benchmark([50, 200], cases, repeats=2, verbose=False)
        assert len(res) == 4
        assert (res["median_s"] > 0).all()
        ax = benchmark.plot_benchmark(res)
        assert ax.get_xscale() == "log"
