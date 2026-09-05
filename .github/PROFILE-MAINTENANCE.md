# Profile maintenance

The README uses repository-owned SVGs so profile visitors do not depend on public
stats-card servers, badge services, or Vercel deployments. The rice-field hero is
preserved from commit `86fd938`; identity, featured project, footer, and activity
cards live in `assets/`. Edit the first three SVGs directly to change their copy.

`Refresh profile activity` runs daily at 00:17 UTC and can be run manually from
Actions. It queries GitHub GraphQL with the built-in `github.token`, then commits
only `assets/activity.svg`. No PAT or Vercel account is needed. Counts and the
calendar cover GitHub's default last-year window and follow profile visibility
settings; they do not claim to include all private commits. A failed API request
or invalid response fails the workflow before replacing the last good image.
The visible update date makes stale data apparent. The snake remains managed by
its existing workflow and `output` branch.

Local refresh (Python 3.10+ and authenticated GitHub CLI):

```sh
python3 -m unittest discover -s scripts -v
python3 scripts/update_activity.py
```

`Validate profile` checks the renderer's error handling, SVG syntax, and asset
references on pull requests. New projects should link to real repositories and
PRs; distinguish a contributor fork and a proposed PR from work merged upstream.

To undo this refresh, revert its merge commit. There are no external deployments,
new secrets, or paid services to remove. Disable the activity workflow in Actions
if automatic updates are no longer wanted.
