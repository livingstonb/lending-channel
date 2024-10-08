close all
p = params_fn();

bank = struct();
bank.deposits = 1;

nonbank = struct();
nonbank.drawn = 0.2;
nonbank.limit = 0.5;


nonbank.committed = nonbank.limit - nonbank.drawn;

x = 0.6:0.01:1;
bank.deposits = x;

bank.reserves0 = bank.deposits - nonbank.drawn;

% x = 1:0.01:1.5;
% plot(x, lcr_cost_fn(p, x))

prof_maintain = profits_maintain_line(p, bank, nonbank);
prof_call = profits_call_line(p, bank, nonbank);
plot(x, prof_maintain)
hold on
plot(x, prof_call)
xlabel("deposits")
ylabel("profits")
legend(["Profits, maintain line", "Profits, call line"])


function params = params_fn()
    params = struct();
    params.riskfree = 0.02;
    params.sprd_committed = 0.01;
    params.sprd_drawn = 0.04;
    params.sprd_deposits = -0.01;
    params.ploan = 1.02;
    params.haircut = 0.05;
    params.outflow_committed = 0.4;
    params.outflow_deposits = 0.05;
    params.lcr_penalty = 5e-2;
    params.lcr_curve = 1.8;

    % Interest rates
    params.r_committed = params.riskfree + params.sprd_committed;
    params.r_drawn = params.riskfree + params.sprd_drawn;
    params.r_deposits = params.riskfree + params.sprd_deposits;
end

function pi_maintain = profits_maintain_line(p,...
    bank, nonbank)

    netinterest = p.r_drawn * nonbank.drawn...
        + p.r_committed * nonbank.committed...
        + p.riskfree * bank.reserves0 - p.r_deposits * bank.deposits;
    lcr = lcr_fn(p, bank.reserves0, nonbank.committed, bank.deposits);

    pi_maintain = netinterest - lcr_cost_fn(p, lcr);
end

function pi_call = profits_call_line(p,...
    bank, nonbank)

    proceeds_collateral = (p.ploan - 1) ./ (1 - p.haircut)...
        .* nonbank.drawn;
    reserves = bank.reserves0 + proceeds_collateral;
    
    committed = 0;
    lcr = lcr_fn(p, reserves, committed, bank.deposits);

    pi_call = proceeds_collateral - lcr_cost_fn(p, lcr)...
        + p.riskfree .* reserves - p.r_deposits * bank.deposits;
end

function lcr = lcr_fn(p, reserves, committed, deposits)
    hqla = reserves;
    outflow = p.outflow_committed .* committed ...
        + p.outflow_deposits .* deposits;
    lcr = hqla ./ outflow;
end

function lcr_cost = lcr_cost_fn(p, lcr)
    lcr_cost = p.lcr_penalty ./ (lcr - 1) .^ p.lcr_curve;
end
