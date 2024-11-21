import Link from "next/link";
import axios from "axios";
import {cookies} from "next/headers";


export default async function asd() {
    const user = await axios.get(`${process.env.BACKEND_HOST}/Accounts/Me`, {
        headers: {
            Cookie: `access_token=${(await cookies()).get('access_token').value}`
        }
    }).then((res) => res.data)
    return (
        <div>
            <h1>{user.username}</h1>
            <Link href="/login">login</Link>
        </div>
    )
}