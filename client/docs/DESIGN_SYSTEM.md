# Design System

The redesign combines institutional publishing, documentation, and restrained enterprise UI. Editorial content uses Georgia/system serif. Interface controls use Segoe UI/system sans. Identifiers use Cascadia Mono/Consolas. These stacks are centralized as `--font-body`, `--font-ui`, and `--font-mono`.

The visual system is mostly off-white, white, and gray. Dark and light greens carry identity and action meaning. Blue underlined links are deliberately used for knowledge navigation. Radii are 2, 4, and 7 pixels rather than large soft containers. Layout relies on rules, tables, indexes, and whitespace more than repeated cards.

Three themes are supported: light neutral, warm beige, and deep graphite. The dark theme deliberately avoids green-washed surfaces. Theme controls cycle through all three and persist the choice locally. Selection colors, contextual menus, search, mega-navigation, and the VscCursor-based pointer derive their treatment from active tokens.

Sparse square grids are generated in CSS and used behind primary public-page introductions. Missing-grid areas and low-opacity borders prevent the motif from becoming a continuous engineering-paper background. A restrained diagonal divider token is available for selective Abyssinian-inspired section rhythm.

Tokens cover colors, surfaces, text, borders, shadows, link, focus, fonts, radius, section spacing, and durations. Motion is brief and orientation-focused; reduced-motion disables transitions and animation.
