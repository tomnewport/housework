import { useCallback, useEffect, useState } from "react";
import { useRespondOtpMutation, useSendOtpMutation } from "../../services/housework/auth";
import { Alert, Button, Link, TextField, Typography } from "@mui/material";
import { FetchBaseQueryError } from "@reduxjs/toolkit/query";
import { SerializedError } from "@reduxjs/toolkit";

function getError(error: FetchBaseQueryError | SerializedError | undefined) {
    if (error && "data" in error) {
        const data = error.data as Record<string, string>;
        switch (data.detail) {
            case "OTP challenge not open": return "Code does not exist."
            case "OTP challenge expired": return "Code has expired."
            case "OTP challenge not set": return "Code does not exist."
            case "OTP not matched": return "Code does not match."
            case "OTP sub not set": return "Code does not exist."
            default: return "Unknown problem with code."
        }
    }
    return null;
}

export default function OtpLogin({ sub, onQuit }: { sub: string, onQuit: () => void}) {
    const [respondOtp, {error: otpError, reset, isUninitialized}] = useRespondOtpMutation();
    const [resendOtp, {isLoading:resendLoading} ] = useSendOtpMutation()
    const [otp, setOtp] = useState('');

    useEffect(() => {
        if (otp.length === 6 ) respondOtp(otp);
    }, [otp, respondOtp])

    const handleResend = useCallback(async () => {
        setOtp('');
        resendOtp(sub);
        reset();
    }, [resendOtp, sub, reset]);

    const error = isUninitialized ? null : getError(otpError);

    console.log(isUninitialized, otpError);

    return (
        <>
            <Typography variant="body1" gutterBottom>
                A code has been sent by email to <strong>{sub}</strong>. Please enter it to continue. <Link href="#" onClick={onQuit}>Click here</Link> to try a different email, or log in using a password.
            </Typography>
            {error && <Alert sx={{ mt: 2, mb: 3 }} severity="error">{error} Would you like to <Link href="#" onClick={handleResend}>send another code?</Link></Alert>}
            <TextField inputProps={{ style: { textAlign: 'center', fontSize: '1.5rem'}}} error={error!== null} value={otp} onChange={e => setOtp(e.target.value)} />
            
        </>
    )
}

