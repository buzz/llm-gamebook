import { Link, useRoute } from 'wouter'
import type { LinkProps } from 'wouter'

import BasicNavLink, { type BasicNavLinkProps } from './BasicNavLink'

type RouterNavLinkProps = BasicNavLinkProps & LinkProps

function RouterNavLink(props: RouterNavLinkProps) {
  const [isActive] = useRoute(props.to ?? '')

  return <BasicNavLink active={isActive} component={Link} {...props} />
}

export default RouterNavLink
