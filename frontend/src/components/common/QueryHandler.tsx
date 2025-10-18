import { Center, Loader } from '@mantine/core'
import type { BaseQueryFn, TypedUseQueryHookResult } from '@reduxjs/toolkit/query/react'
import type { ReactNode } from 'react'

import { isApiQueryError } from '@/types/api'

import ErrorAlert from './ErrorAlert'
import NotFound from './NotFound'

interface QueryHandlerProps<R, Q, B extends BaseQueryFn> {
  children: (data: R) => ReactNode
  notFoundTitle: string
  notFoundMessage: string
  result: TypedUseQueryHookResult<R, Q, B>
}

function QueryHandler<R, Q, B extends BaseQueryFn>({
  children,
  notFoundTitle,
  notFoundMessage,
  result: { data, error, isFetching },
}: QueryHandlerProps<R, Q, B>) {
  if (isFetching) {
    return (
      <Center h="100%">
        <Loader size="xl" />
      </Center>
    )
  }

  if (error) {
    if (isApiQueryError(error) && error.status === 404) {
      return <NotFound title={notFoundTitle} message={notFoundMessage} />
    }
    return <ErrorAlert error={error} />
  }

  return data ? children(data) : null
}

export default QueryHandler
