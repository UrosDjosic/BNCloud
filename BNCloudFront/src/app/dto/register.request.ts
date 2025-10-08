export interface RegisterRequest{
    username : string,
    email: string,
    password: string,
    firstName : string,
    lastName : string,
    birthDate : string,
}

export function createRegisterRequest(): RegisterRequest{
    return{
        username : '',
        email: '',
        password: '',
        firstName: '',
        lastName: '',
        birthDate: ''
    }
}