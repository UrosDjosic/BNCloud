export interface VerificationRequest{
    username : string,
    code: string,
}

export function createRegisterRequest(): VerificationRequest{
    return{
        username : '',
        code: ''
    }
}