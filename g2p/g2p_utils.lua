-- Utils specific to g2p

------------------------------------------------------------------------------------------
-- Utilities to convert batcher encoded inputs and targets back into words and phonemes
------------------------------------------------------------------------------------------
-- Convert input (word encoded as tensor) back to word so we can compare against predictions
-- batchsize x batch_seq_len x input_dim
function convert_inputs_to_words(inputs, sizes, idx_to_grapheme)
	local words = {}
	for i=1,inputs:size(1) do 								-- 1 to batchsize
		local word = ''
		local one_hot_word = inputs[{{i},{},{}}]			-- one hot encoded: 1 x batch_seq_len x input_dim
		local maxs, indices = torch.max(one_hot_word, 3)
		-- print(sizes)
		-- print(i)
		for j=1,sizes[i] do
			local idx = indices[1][j][1]
			word = word .. idx_to_grapheme[idx]
		end
		table.insert(words, word)
	end
	return words
end

-- Convert target to phonemes so we can compare against predictions
-- tbl = {1: 16, 2: 12, 3: 20}
function convert_targets_to_phonemes(targets, idx_to_phoneme)
	local phonemes = {}
	for i, encoded_phonemes in ipairs(targets) do
		local phoneme_seq = {}
		for j=1, #encoded_phonemes do
			local idx = encoded_phonemes[j]
			table.insert(phoneme_seq, idx_to_phoneme[idx])
		end
		table.insert(phonemes, phoneme_seq)
	end
	return phonemes
end

-- Decode predictions (tensor)
function convert_preds_to_phonemes(predictions, sizes, idx_to_phoneme)
	local preds = {}

	-- Pluck out most likely phonemes by argmaxing over activations
	local maxs, indices = torch.max(predictions, 3)
	for i=1,indices:size(2) do					-- 1 to batchsize
		local cur_pred = {}
		local prev_phoneme = '-'				-- To decode CTC, can't have same token twice in a row
		for j=1,sizes[i] do
			local idx = indices[j][i][1]
			idx = idx - 1						-- warp-CTC indexing starts at 0 (where 0 is the blank character)
			local phoneme = idx_to_phoneme[idx]
			if phoneme ~= '-' and phoneme ~= prev_phoneme then
				table.insert(cur_pred, phoneme)
				prev_phoneme = phoneme
			end
		end
		table.insert(preds, cur_pred)
	end
	return preds
end
