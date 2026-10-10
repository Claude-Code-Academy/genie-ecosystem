# Member access and private updates

Members start with [one guide and its copy/paste prompt](getting-started.md).
The guide is public so an agent can read it before GitHub sign-in. Product
packages remain private. This page explains that access boundary; it does not
change repository permissions or licenses.

## Granting access

Invite the member's own GitHub account to the Academy organization and give it
read access to the intended member repositories, normally through a member team.
They must accept the invitation. Organization membership and a successful
`gh auth login` are not substitutes for the actual repository grant; organization
base permissions, teams, direct grants and SSO can affect effective access.
Keep maintainer-only repositories outside the member grant.

For the published **v0.1.0-alpha.1 portable installer**, the required private
download comes from `Claude-Code-Academy/genie-aios`. Its verified Core envelope
contains Core plus Content OS, Mobile OS and Web OS artifacts. Therefore access
to that envelope gives access to those included artifacts; **this release does
not enforce a separate entitlement for each department's source repository**.
Setup activates only selected departments. Members need separate repository
access if they want to clone those product sources or use the optional native
marketplaces/library/second-brain kit. Future release packaging may change this;
recheck [release metadata](../bootstrap-release.json) and the authenticated
release assets when changing membership tiers.

The member authenticates as themselves using native GitHub CLI browser sign-in.
Setup separately tests private Core access. Do not distribute a maintainer PAT,
use a shared GitHub identity, or save `gh auth token` output in a shell profile.
Some old native marketplace guides recommend persistent token exports; that is
not part of this portable flow. Keep native authentication under its supported
credential storage and resolve optional integrations individually.

## When a member leaves

**Yes: removing all effective private-repository access prevents that account
from fetching future private source changes and private release downloads.**
The public guide and public version metadata remain readable. A private update
download then fails authentication/authorization rather than granting access
through the public launcher.

Review every effective grant: organization membership, member teams, other
teams, direct/outside-collaborator grants, any separately accessible private
forks, and separately shared credentials or service access. Removing only one
team is insufficient if another grant remains. Do not use conversion to outside
collaborator as shorthand for revocation: it can retain repository access.
See GitHub's documentation on [removing an organization member](https://docs.github.com/en/organizations/managing-membership-in-your-organization/removing-a-member-from-your-organization),
[removing a team member](https://docs.github.com/en/organizations/organizing-members-into-teams/removing-organization-members-from-a-team)
and [conversion to outside collaborator](https://docs.github.com/en/organizations/managing-user-access-to-your-organizations-repositories/managing-outside-collaborators/converting-an-organization-member-to-an-outside-collaborator).

**Revocation does not erase local copies or disable already downloaded code.**
Clones, installed packages, backups and cached release envelopes can remain on
the former member's machine. A cached envelope may include departments they had
not activated. Genie has no remote kill switch or continual membership check for
offline execution. GitHub likewise documents that local copies can remain after
access removal. Blocking future distribution and remotely disabling existing
software are different capabilities.

The private first-party repositories have membership-dependent license terms,
including restrictions on use after membership ends and a requirement to delete
copies. Those terms are separate from technical enforcement. Read the applicable
[AIOS license](https://github.com/Claude-Code-Academy/genie-aios/blob/main/LICENSE),
[Content marketplace license](https://github.com/Claude-Code-Academy/genie-plugin-marketplace/blob/main/LICENSE),
[Mobile license](https://github.com/Claude-Code-Academy/genie-mobile-os/blob/main/LICENSE)
and [Web license](https://github.com/Claude-Code-Academy/genie-web-os/blob/main/LICENSE).
Third-party tools, public assets and individual templates may have different
licenses; do not apply the proprietary first-party terms to the entire ecosystem.

## Evidence and recheck

Checked **2026-10-10** against the organization repository inventory, the published
Core envelope, installer source and the linked GitHub documentation. This is an
access-model review, not a live removal test on a community member. No member
permissions were changed. For an actual offboarding, verify the effective grants
and denied private access using the account concerned; do not treat a maintainer's
successful download as proof of a member's permissions.
