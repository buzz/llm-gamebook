import { Link, useRoute } from 'wouter'
import type { LinkProps } from 'wouter'

import CollapsibleNavLink from './CollapsibleNavLink'
import type { CollapsibleNavLinkProps } from './CollapsibleNavLink'

type RouterNavLinkProps = CollapsibleNavLinkProps & LinkProps

function RouterNavLink(props: RouterNavLinkProps) {
  const [isActive] = useRoute(props.to ?? '')

  return <CollapsibleNavLink active={isActive} component={Link} {...props} />
}

export default RouterNavLink
