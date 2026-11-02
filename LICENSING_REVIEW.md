# Preliminary licensing review — 2026-11-02

## Scope and conclusion

Reviewed the current source tree at ef2607e14354509aa0d4108d47628e899bafbab9, installer dependencies, license, display integration and cursor patch. This is a technical licensing review, not a lawyer's legal opinion or comprehensive clearance. It does not certify absence of infringement, patents, trademark conflicts, or originality of AI-assisted code.

No definite copyright violation was identified in the reviewed source distribution. This does not establish that every dependency in every user's installed environment is compliant. The repository does not include a packaged runtime, noVNC vendor directory, proprietary image assets or an installed Python environment. The UI uses text/emoji and system fonts rather than bundled commercial font files.

## Verified sources

- noVNC v1.6.0 LICENSE.txt and docs/LICENSE.MPL-2.0, read at their tagged GitHub source.
- websockify v0.13.0 COPYING and setup.py, read at their tagged GitHub source.
- KDE's Krfb application page identifies GPL-2.0+; distro-specific builds and all per-file licenses were not exhaustively audited.
- Mozilla's current MPL 2.0 FAQ: https://www.mozilla.org/en-US/MPL/2.0/FAQ/

## Improvements made

Added THIRD_PARTY_NOTICES.md, a verbatim MPL 2.0 reference copy, explicit MPL terms for modifications to noVNC, and links in the Display UI to the actual installed modified source and upstream license. Clarified the root MIT license does not cover all dependencies. The installer already retains noVNC's upstream notices.

## Name screening: unresolved

Searches for Side Panel and SidePanel found existing software uses, including:
- https://www.sidepanel.com/ — branded Sidepanel with a link to an app.
- https://github.com/band-app/sidepanel — Band Side Panel, a macOS launcher.
- https://chromewebstore.google.com/detail/sidepanel-multitask-bookm/jlfdjcmofednlaankkfgcokeacnjjjpg — a similarly named browser extension.

These are leads, not findings of trademark ownership or infringement. No claim is made about registration status, priority, territory, similarity of goods or likelihood of confusion. The Canadian Trademarks Database search page was accessible, but a reliable completed register query was not obtained. USPTO/WIPO searches and common-law clearance were not completed. The name is therefore NOT cleared. Do not represent this report as proof that it is available.

Canadian search portal: https://ised-isde.canada.ca/cipo/trademark-search/srch?lang=eng
CIPO guidance: https://www.ised-isde.canada.ca/site/canadian-intellectual-property-office/en/trademarks/general-information

## Before distributing a bundled installer

1. Freeze the actual package and transitive dependency versions and create a full license/source inventory.
2. Include the notices, license texts and corresponding source required by those exact components, including any bundled runtimes, fonts and assets.
3. Preserve access to the modified noVNC source matching the shipped client.
4. Review any changed linking, packaging or distribution model for GPL/LGPL obligations.
5. Complete trademark clearance for intended territories, or select and check a more distinctive name.
6. Review code provenance; this review is not a global similarity scan or a conclusion about copyright ownership in AI-generated output.

The existing source beta and a future bundled binary are separate audit scopes. Changes to dependencies, artwork, branding or distribution require reassessment.
