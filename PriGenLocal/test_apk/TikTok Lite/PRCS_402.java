/*Application Package Name: com.tiktok.lite.go
class PRCS_402 {
/**
X.40e;L(Ljava/lang/String; Lorg/json/JSONObject;)V
*/

    public static void L(String p22, org.json.JSONObject p23)
    {
        try {
            android.accounts.Account[] v14_1;
            android.accounts.AccountManager v9 = android.accounts.AccountManager.get(X.16B.LB);
            com.bytedance.helios.statichook.api.HeliosApiHook v4_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            int v0_1 = 1;
            Object[] v10 = new Object[1];
            v10[0] = "com.google";
            com.bytedance.helios.statichook.api.ExtraInfo v11_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;)[Landroid/accounts/Account;", "dzBzEhEpEcvSUUUuTBbKc9NnF3kueWo2KOurYJDb0ibEEftgpwxkw68pqpAxGKmGaTKGsgU6I5UdbinR");
            org.json.JSONObject v2_0 = v4_1.preInvoke(102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, "android.accounts.Account[]", v11_1);
        } catch (Exception) {
            return;
        }
        if (!v2_0.intercept) {
            v14_1 = v9.getAccountsByType("com.google");
            v4_1.postInvoke(v14_1, 102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, v11_1, 1);
        } else {
            v4_1.postInvoke(0, 102501, "android/accounts/AccountManager", "getAccountsByType", v9, v10, v11_1, 0);
            v14_1 = ((android.accounts.Account[]) v2_0.returnValue);
        }
        if ((v14_1.length == 0) || (!kotlin.jvm.internal.Intrinsics.L(p22, v14_1[0].name))) {
            v0_1 = 0;
        }
        X.4FU.L("login_params_check", v0_1, p23);
        return;
    }

/**
X.42a;onClick(Landroid/view/View;)V
*/

    public final void onClick(android.view.View p9)
    {
        int v7;
        String v4 = this.L.getText().toString();
        String v5 = this.LB.getText().toString();
        X.40e.L(v4, new X.4D8().LB());
        if ((android.text.TextUtils.isEmpty(v4)) || ((android.text.TextUtils.isEmpty(v5)) || ((!kotlin.jvm.internal.Intrinsics.L(v4, this.LFFFF)) || (!kotlin.jvm.internal.Intrinsics.L(v5, this.LFFL))))) {
            v7 = 0;
        } else {
            v7 = 1;
        }
        int v3;
        boolean v1 = X.40m.L(v4);
        boolean v0_13 = ((com.ss.android.ugc.aweme.login.viewmodel.LoginViewModel) this.LFFLLL.getValue());
        if (!v0_13) {
            v3 = 0;
        } else {
            v3 = v0_13.LCI;
        }
        String v6;
        if (!v1) {
            v6 = "handle";
        } else {
            v6 = "email";
        }
        X.44k.L(this, v3, v4, v5, v6, v7);
        return;
    }


}