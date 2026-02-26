import '@mantine/core'

declare module '@mantine/core' {
  export interface MantineThemeOther {
    fontFamilySerif: string
    textShadowLight: string
    textShadowDark: string
  }
}
