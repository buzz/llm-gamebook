import '@fontsource/spectral/300'
import '@fontsource/spectral/300-italic'
import '@fontsource/spectral/700'
import '@fontsource/spectral/700-italic'
import './theme.css'

import { Badge, createTheme, getThemeColor } from '@mantine/core'
import type { CSSVariablesResolver } from '@mantine/core'

import COLORS from './colors'

const themeOverride = createTheme({
  colors: COLORS,
  primaryColor: 'indigo',

  components: {
    Badge: Badge.extend({
      vars: (theme, props) => {
        if (props.color) {
          const badgeColor = `color-mix(in srgb, ${getThemeColor(props.color, theme)} 25%, white)`
          return { root: { '--badge-color': badgeColor } }
        }
        return { root: {} }
      },
    }),
  },

  other: {
    fontFamilySerif: "Spectral, Charter, 'Bitstream Charter', 'Sitka Text', Georgia, serif",
    textShadowLight: '0 1px 0 hsl(0deg 0% 100% / 30%)',
    textShadowDark: '0 1px 0 hsl(0deg 0% 0% / 30%)',
  },
})

const cssVariablesResolver: CSSVariablesResolver = (theme) => ({
  variables: {
    '--mantine-font-family-serif': theme.other.fontFamilySerif,
  },
  light: {
    '--llmg-text-shadow': theme.other.textShadowLight,
  },
  dark: {
    '--llmg-text-shadow': theme.other.textShadowDark,
  },
})

export { cssVariablesResolver, themeOverride }
