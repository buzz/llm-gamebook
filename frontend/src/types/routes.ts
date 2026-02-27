import type { ComponentType } from 'react'

import type { ROUTES } from '@/routes/routes'

interface RouteDef {
  path: string
  component: ComponentType
}

type RouteName = keyof typeof ROUTES

type Compute<T> = { [K in keyof T]: T[K] }

/** Extract keys from "(?<key>...)" patterns in a string. */
type ExtractParams<S extends string> = S extends `${string}(?<${infer Key}>${string})${infer Rest}`
  ? Compute<{ [K in Key]: string } & ExtractParams<Rest>>
  : unknown

/** Extract route parameters for named route. */
type RouteParams<T extends RouteName> = [ExtractParams<(typeof ROUTES)[T]['path']>] extends [
  infer P,
]
  ? unknown extends P
    ? never
    : P
  : never

export type { RouteDef, RouteName, RouteParams }
