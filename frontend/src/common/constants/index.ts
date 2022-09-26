const title = 'Интернет-магазин Linetok, г. Рогачев.' as const
const description = `Интернет-магазин Linetok.by в г. Рогачев -
онлайн площадка бытовой техники, электроники, товаров для дома и дачи.
Следите за нашими акциями и промокодами. С нами выгодно!` as const

export const API_URL = 'http://localhost:8000/api/' as const

export const API = {
  auth: '/auth/token',
  products: '/products',
  users: '/users'
} as const

export const SEO = {
  description,
  title
} as const
