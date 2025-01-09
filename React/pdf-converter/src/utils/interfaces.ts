import { Dayjs } from "dayjs"

export interface ITokenObj {
    refreshtoken:string,
    accessToken: string,
    expiryDate: Dayjs
}

export interface IclientObj {
    value: string,
    label: string
}